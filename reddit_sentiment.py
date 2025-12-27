"""
Reddit Sentiment Analysis Module
Analyzes mentions and sentiment from WallStreetBets and investing subreddits

Note: This uses public Reddit JSON API (no authentication required)
For higher rate limits, consider setting up Reddit API credentials
"""

import requests
from datetime import datetime, timedelta
import time
from urllib.parse import quote
import signal
from contextlib import contextmanager

# User agent for requests
USER_AGENT = "Mozilla/5.0 (compatible; StockAnalyzer/1.0)"

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    """Context manager to enforce timeout on operations"""
    def signal_handler(signum, frame):
        raise TimeoutException("Operation timed out")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def search_reddit_json(subreddit, query, limit=25):
    """
    Search Reddit using public JSON API (no auth required)
    
    Args:
        subreddit: Subreddit name
        query: Search query
        limit: Max results (default: 25)
        
    Returns:
        List of posts
    """
    try:
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',
            'sort': 'new',
            'limit': limit,
            't': 'day'
        }
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            posts = []
            
            for child in data['data']['children']:
                post = child['data']
                posts.append({
                    'title': post.get('title', ''),
                    'score': post.get('score', 0),
                    'upvote_ratio': post.get('upvote_ratio', 0.5),
                    'num_comments': post.get('num_comments', 0),
                    'created_utc': post.get('created_utc', 0),
                    'permalink': post.get('permalink', ''),
                    'selftext': post.get('selftext', '')[:200]  # First 200 chars
                })
            
            return posts
        else:
            return []
            
    except Exception as e:
        return []


def get_reddit_sentiment(ticker_symbol, hours=24, max_posts=100):
    """
    Get Reddit sentiment for a ticker from multiple subreddits
    
    Args:
        ticker_symbol: Stock ticker (e.g., 'AAPL')
        hours: Look back period in hours (default: 24)
        max_posts: Maximum posts to analyze per subreddit (default: 100)
        
    Returns:
        dict with sentiment analysis
    """
    
    try:
        # Enforce 15 second timeout for entire Reddit API operation
        with time_limit(15):
            return _get_reddit_sentiment_internal(ticker_symbol, hours, max_posts)
    except TimeoutException:
        # Return neutral sentiment on timeout
        return {
            'available': True,
            'ticker': ticker_symbol.upper(),
            'mentions': 0,
            'sentiment': 'NEUTRAL',
            'score': 0,
            'confidence': 0,
            'engagement': 0,
            'message': f'Reddit API timeout (>15s) - using NEUTRAL'
        }
    except Exception as e:
        # Return neutral sentiment on any error
        return {
            'available': True,
            'ticker': ticker_symbol.upper(),
            'mentions': 0,
            'sentiment': 'NEUTRAL',
            'score': 0,
            'confidence': 0,
            'engagement': 0,
            'message': f'Reddit API error: {str(e)}'
        }


def _get_reddit_sentiment_internal(ticker_symbol, hours=24, max_posts=100):
    """Internal function with actual Reddit API logic"""
    
    ticker = ticker_symbol.upper()
    
    # Subreddits to search
    subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
    
    mentions = []
    total_upvotes = 0
    total_comments = 0
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_timestamp = cutoff_time.timestamp()
    
    # Search each subreddit
    for sub_name in subreddits:
        try:
            # Search for ticker with $ or plain ticker
            search_query = f"${ticker} OR {ticker}"
            posts = search_reddit_json(sub_name, search_query, limit=max_posts)
            
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
            
            for post in posts:
                # Check if post is within time window
                if post['created_utc'] < cutoff_timestamp:
                    continue
                
                # Extract mention details
                mention = {
                    'title': post['title'],
                    'score': post['score'],
                    'upvote_ratio': post['upvote_ratio'],
                    'num_comments': post['num_comments'],
                    'created': datetime.fromtimestamp(post['created_utc']),
                    'subreddit': sub_name,
                    'url': f"https://reddit.com{post['permalink']}"
                }
                
                mentions.append(mention)
                total_upvotes += post['score']
                total_comments += post['num_comments']
                
        except Exception as e:
            # Subreddit might have issues, continue to next
            continue
    
    # Analyze sentiment
    if not mentions:
        return {
            'available': True,
            'ticker': ticker,
            'mentions': 0,
            'sentiment': 'NEUTRAL',
            'score': 0,
            'confidence': 0,
            'engagement': 0,
            'message': f'No recent mentions of {ticker} on Reddit (last {hours}h)'
        }
    
    # Calculate sentiment based on engagement and keywords
    bullish_keywords = ['buy', 'calls', 'moon', 'rocket', '🚀', 'bullish', 'long', 'pump', 'squeeze', 'rally', 'breakout']
    bearish_keywords = ['sell', 'puts', 'crash', 'dump', 'bearish', 'short', 'overvalued', 'bubble', 'fall', 'drop']
    
    bullish_count = 0
    bearish_count = 0
    
    for mention in mentions:
        title_lower = mention['title'].lower()
        
        # Weight by engagement (upvotes + comments)
        weight = (mention['score'] + mention['num_comments']) / 10
        weight = max(1, min(weight, 10))  # Cap between 1-10
        
        # Count keywords
        for keyword in bullish_keywords:
            if keyword in title_lower:
                bullish_count += weight
        
        for keyword in bearish_keywords:
            if keyword in title_lower:
                bearish_count += weight
    
    # Calculate sentiment score (-100 to +100)
    total_sentiment = bullish_count + bearish_count
    if total_sentiment > 0:
        sentiment_score = ((bullish_count - bearish_count) / total_sentiment) * 100
    else:
        sentiment_score = 0
    
    # Determine sentiment label
    if sentiment_score > 30:
        sentiment_label = 'BULLISH'
    elif sentiment_score < -30:
        sentiment_label = 'BEARISH'
    else:
        sentiment_label = 'NEUTRAL'
    
    # Calculate engagement score (normalized)
    avg_upvotes = total_upvotes / len(mentions)
    avg_comments = total_comments / len(mentions)
    engagement_score = min(100, (avg_upvotes + avg_comments * 2) / 2)
    
    # Confidence based on sample size and engagement
    confidence = min(100, (len(mentions) / (max_posts/4)) * 50 + engagement_score / 2)
    
    # Sort mentions by engagement (top 5)
    top_mentions = sorted(mentions, key=lambda x: x['score'] + x['num_comments'], reverse=True)[:5]
    
    return {
        'available': True,
        'ticker': ticker,
        'mentions': len(mentions),
        'sentiment': sentiment_label,
        'score': round(sentiment_score, 1),
        'confidence': round(confidence, 1),
        'engagement': round(engagement_score, 1),
        'total_upvotes': total_upvotes,
        'total_comments': total_comments,
        'bullish_signals': round(bullish_count, 1),
        'bearish_signals': round(bearish_count, 1),
        'top_posts': [
            {
                'title': m['title'][:100],
                'score': m['score'],
                'comments': m['num_comments'],
                'subreddit': m['subreddit']
            }
            for m in top_mentions
        ],
        'message': f"Found {len(mentions)} mentions in last {hours}h - {sentiment_label} sentiment"
    }


def get_sentiment_summary(reddit_data):
    """
    Generate human-readable summary of Reddit sentiment
    
    Args:
        reddit_data: Result from get_reddit_sentiment()
        
    Returns:
        Formatted string summary
    """
    if not reddit_data.get('available'):
        return f"⚠️ Reddit sentiment unavailable"
    
    if reddit_data['mentions'] == 0:
        return f"📱 Reddit: No recent activity for {reddit_data['ticker']}"
    
    sentiment = reddit_data['sentiment']
    emoji_map = {
        'BULLISH': '🚀',
        'BEARISH': '🐻',
        'NEUTRAL': '😐'
    }
    emoji = emoji_map.get(sentiment, '❓')
    
    summary = []
    summary.append(f"\n📱 Reddit Sentiment Analysis:")
    summary.append(f"   • Mentions (24h): {reddit_data['mentions']}")
    summary.append(f"   • Sentiment: {emoji} {sentiment} (score: {reddit_data['score']:+.1f})")
    summary.append(f"   • Confidence: {reddit_data['confidence']:.0f}%")
    summary.append(f"   • Engagement: {reddit_data['engagement']:.0f}/100")
    summary.append(f"   • Total Upvotes: {reddit_data['total_upvotes']:,}")
    
    if reddit_data.get('top_posts'):
        summary.append(f"\n   Top Posts:")
        for i, post in enumerate(reddit_data['top_posts'][:3], 1):
            summary.append(f"   {i}. [{post['subreddit']}] {post['title']} ({post['score']}↑ {post['comments']}💬)")
    
    return "\n".join(summary)


def analyze_wsb_hype(ticker_symbol):
    """
    Quick check if ticker is currently trending on WSB
    
    Args:
        ticker_symbol: Stock ticker
        
    Returns:
        dict with hype level
    """
    reddit_data = get_reddit_sentiment(ticker_symbol, hours=12, max_posts=50)
    
    if not reddit_data.get('available') or reddit_data['mentions'] == 0:
        return {
            'is_hyped': False,
            'hype_level': 0,
            'message': 'No significant WSB activity'
        }
    
    # Hype detection thresholds
    mentions = reddit_data['mentions']
    engagement = reddit_data['engagement']
    
    if mentions >= 20 and engagement >= 60:
        hype_level = 'HIGH'
        is_hyped = True
    elif mentions >= 10 and engagement >= 40:
        hype_level = 'MODERATE'
        is_hyped = True
    elif mentions >= 5:
        hype_level = 'LOW'
        is_hyped = False
    else:
        hype_level = 'NONE'
        is_hyped = False
    
    return {
        'is_hyped': is_hyped,
        'hype_level': hype_level,
        'mentions': mentions,
        'engagement': engagement,
        'sentiment': reddit_data['sentiment'],
        'message': f"{hype_level} hype detected" if is_hyped else "Normal activity"
    }


if __name__ == '__main__':
    # Test with popular tickers
    test_tickers = ['TSLA', 'NVDA', 'AAPL']
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Testing: {ticker}")
        print('='*60)
        
        sentiment = get_reddit_sentiment(ticker)
        print(get_sentiment_summary(sentiment))
        
        hype = analyze_wsb_hype(ticker)
        print(f"\n🔥 Hype Check: {hype['message']}")
