"""
Agente de análisis financiero potenciado por Gemini API
Realiza análisis profundo de noticias y genera recomendaciones con IA
"""

import os
import json
from datetime import datetime
from colorama import Fore, Style

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

import market_data


class LLMFinancialAgent:
    """
    Agente financiero que usa Gemini API para análisis profundo
    """
    
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai no está instalado.\n"
                "Instala con: pip install google-generativeai"
            )
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY no configurada.\n"
                "Configura con: export GEMINI_API_KEY='your_key_here'\n"
                "Obtén tu API key en: https://aistudio.google.com/apikey"
            )
        
        # Configurar Gemini
        genai.configure(api_key=self.api_key)
        # Usar gemini-2.0-flash (modelo más reciente y rápido)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    def run_llm_analysis(self):
        """
        Ejecuta análisis completo usando Gemini API
        """
        print(f"{Fore.CYAN}Recopilando datos para análisis con IA...{Style.RESET_ALL}")
        
        # Obtener datos del mercado
        try:
            ticker_obj = market_data.get_ticker_data(self.ticker)
            fundamentals = market_data.get_fundamental_info(ticker_obj)
            history = market_data.get_historical_data(ticker_obj)
            news = market_data.get_news(ticker_obj)
            macro = market_data.get_macro_data()
        except Exception as e:
            print(f"{Fore.RED}Error obteniendo datos: {str(e)}{Style.RESET_ALL}")
            return {"error": str(e)}
        
        current_price = fundamentals.get('currentPrice', history['Close'].iloc[-1])
        
        # Construir prompt para Gemini
        prompt = self._build_analysis_prompt(fundamentals, history, news, macro, current_price)
        
        print(f"{Fore.CYAN}Analizando con Gemini AI...{Style.RESET_ALL}\n")
        
        try:
            # Llamar a Gemini API
            response = self.model.generate_content(prompt)
            analysis = response.text
            
            # Imprimir análisis
            self._print_llm_analysis(analysis, current_price, fundamentals)
            
            return {
                'ticker': self.ticker,
                'current_price': current_price,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"{Fore.RED}Error en análisis con IA: {str(e)}{Style.RESET_ALL}")
            return {"error": str(e)}
    
    def _build_analysis_prompt(self, fundamentals, history, news, macro, current_price):
        """
        Construye el prompt para Gemini
        """
        # Preparar datos fundamentales clave
        fund_summary = f"""
Precio Actual: ${current_price:.2f}
P/E Ratio: {fundamentals.get('trailingPE', 'N/A')}
PEG Ratio: {fundamentals.get('pegRatio', 'N/A')}
Deuda/Capital: {fundamentals.get('debtToEquity', 'N/A')}
ROE: {fundamentals.get('returnOnEquity', 'N/A')}
Dividend Yield: {fundamentals.get('dividendYield', 'N/A')}
Crecimiento Ingresos: {fundamentals.get('revenueGrowth', 'N/A')}
Recomendación Analistas: {fundamentals.get('recommendationKey', 'N/A')}
"""
        
        # Preparar noticias
        news_summary = "\n".join([
            f"- {article.get('title', 'Sin título')}"
            for article in news[:10]
        ]) if news else "Sin noticias recientes"
        
        # Preparar contexto macro
        macro_summary = f"""
VIX: {macro.get('vix', 'N/A')}
Fear & Greed Index: {macro.get('fear_greed_index', 'N/A')}
Tendencia Tasas: {macro.get('tnx_trend', 'N/A')}
"""
        
        # Indicadores técnicos básicos
        sma_50 = history['Close'].rolling(50).mean().iloc[-1]
        sma_200 = history['Close'].rolling(200).mean().iloc[-1]
        
        tech_summary = f"""
Precio vs SMA50: {'Alcista' if current_price > sma_50 else 'Bajista'}
Precio vs SMA200: {'Alcista' if current_price > sma_200 else 'Bajista'}
"""
        
        prompt = f"""Actúa como un analista financiero experto de Wall Street. Analiza la acción {self.ticker} y proporciona una recomendación de inversión clara y fundamentada.

DATOS FUNDAMENTALES:
{fund_summary}

INDICADORES TÉCNICOS:
{tech_summary}

NOTICIAS RECIENTES:
{news_summary}

CONTEXTO MACROECONÓMICO:
{macro_summary}

INSTRUCCIONES:
Proporciona tu análisis en el siguiente formato EXACTO:

VEREDICTO: [FUERTE COMPRA/COMPRA/NEUTRAL/VENTA/FUERTE VENTA]
CONFIANZA: [0-100]%
HORIZONTE: [Corto Plazo/Medio Plazo/Largo Plazo]

RAZONES PARA COMPRAR (3-5 puntos):
- [Punto 1]
- [Punto 2]
- [Punto 3]

RAZONES DE PRECAUCIÓN (2-4 puntos):
- [Punto 1]
- [Punto 2]

ANÁLISIS DE NOTICIAS:
[Análisis profundo de las noticias recientes y su impacto en la acción - 2-3 oraciones]

NIVELES CLAVE:
Stop Loss Sugerido: $[precio]
Objetivo Corto Plazo: $[precio]
Objetivo Largo Plazo: $[precio]

RESUMEN (2-3 oraciones):
[Tu opinión profesional clara y directa sobre si es buen momento para invertir]

Sé específico, directo y basado en datos. No uses disclaimers genéricos."""

        return prompt
    
    def _print_llm_analysis(self, analysis, current_price, fundamentals):
        """
        Imprime el análisis de forma formateada
        """
        print(f"{Fore.CYAN}{'='*80}")
        print(f"ANÁLISIS CON IA: {self.ticker}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Precio Actual: ${current_price:.2f}{Style.RESET_ALL}")
        print(f"Sector: {fundamentals.get('sector', 'N/A')}")
        print(f"Industria: {fundamentals.get('industry', 'N/A')}\n")
        
        print(f"{Fore.CYAN}{'─'*80}")
        print("ANÁLISIS GENERADO POR GEMINI AI")
        print(f"{'─'*80}{Style.RESET_ALL}\n")
        
        # Imprimir análisis con colores
        lines = analysis.split('\n')
        for line in lines:
            if line.startswith('VEREDICTO:'):
                if 'FUERTE COMPRA' in line or 'COMPRA' in line:
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif 'VENTA' in line:
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
            elif line.startswith('CONFIANZA:') or line.startswith('HORIZONTE:'):
                print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
            elif line.startswith('RAZONES PARA COMPRAR'):
                print(f"\n{Fore.GREEN}{line}{Style.RESET_ALL}")
            elif line.startswith('RAZONES DE PRECAUCIÓN'):
                print(f"\n{Fore.YELLOW}{line}{Style.RESET_ALL}")
            elif line.startswith('ANÁLISIS DE NOTICIAS:'):
                print(f"\n{Fore.CYAN}{line}{Style.RESET_ALL}")
            elif line.startswith('NIVELES CLAVE:'):
                print(f"\n{Fore.MAGENTA}{line}{Style.RESET_ALL}")
            elif line.startswith('RESUMEN'):
                print(f"\n{Fore.CYAN}{line}{Style.RESET_ALL}")
            else:
                print(line)
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print("Análisis completado con IA")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}⚠️  Este análisis fue generado por IA y no constituye asesoría financiera.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Realiza tu propia investigación antes de invertir.{Style.RESET_ALL}\n")
