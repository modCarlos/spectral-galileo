
import os
import json
from datetime import datetime
from jinja2 import Template

class ReportGenerator:
    def __init__(self, analysis_result):
        self.result = analysis_result
        # Aceptar tanto 'ticker' como 'symbol' para compatibilidad
        self.ticker = analysis_result.get('ticker') or analysis_result.get('symbol')
        if not self.ticker:
            raise KeyError("analysis_result debe contener 'ticker' o 'symbol'")
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.filename = f"report_{self.ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
    def _get_template(self):
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Spectral Galileo: {{ ticker }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {
            background: radial-gradient(circle at top right, #1e293b, #0f172a);
            color: #f8fafc;
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
        }
        .glass {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        .card-hover:hover {
            border-color: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        .gauge-container {
            position: relative;
            width: 200px;
            height: 100px;
            overflow: hidden;
        }
        .gauge-bg {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            position: absolute;
            top: 0;
        }
        .gauge-fill {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: conic-gradient(from 270deg, #10b981 {{ confidence }}%, transparent 0);
            position: absolute;
            top: 0;
            transform: rotate(-90deg);
        }
        .gauge-cover {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: #0f172a;
            position: absolute;
            top: 20px;
            left: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        .badge-buy { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-sell { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-neutral { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
                <div class="flex items-center gap-3 mb-1">
                    <div class="p-2 bg-blue-600 rounded-lg">
                        <i data-lucide="zap" class="text-white"></i>
                    </div>
                    <h1 class="text-3xl font-bold tracking-tight">Spectral Galileo <span class="text-blue-500 text-sm font-normal">v1.0.0</span></h1>
                </div>
                <p class="text-slate-400">Análisis Inteligente de Activos Financieros</p>
            </div>
            <div class="text-right">
                <p class="text-sm text-slate-500">Generado el: {{ timestamp }}</p>
                <div class="text-2xl font-bold text-white">{{ ticker }} <span class="text-sm font-normal text-slate-400">| {{ format_currency(result.price) }}</span></div>
            </div>
        </header>

        <!-- Main Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <!-- Veredicto Card -->
            <div class="lg:col-span-2 glass rounded-3xl p-8 flex flex-col md:flex-row items-center gap-8 card-hover">
                <div class="flex-shrink-0">
                    <div class="gauge-container">
                        <div class="gauge-bg"></div>
                        <div class="gauge-fill" style="background: conic-gradient(from 270deg, {{ 'rgba(16, 185, 129, 0.8)' if result.strategy.confidence > 0 else 'rgba(239, 68, 68, 0.8)' }} {{ result.strategy.confidence | abs }}%, transparent 0);"></div>
                        <div class="gauge-cover">
                            <span class="text-3xl font-bold">{{ result.strategy.confidence }}%</span>
                            <span class="text-[10px] text-slate-500 uppercase tracking-widest">Confianza</span>
                        </div>
                    </div>
                </div>
                <div class="text-center md:text-left">
                    <span class="px-4 py-1 rounded-full text-sm font-semibold uppercase tracking-wider {{ 'badge-buy' if 'COMPRA' in result.strategy.verdict else 'badge-sell' if 'VENTA' in result.strategy.verdict else 'badge-neutral' }}">
                        {{ result.strategy.verdict }}
                    </span>
                    <h2 class="text-2xl font-bold mt-3 mb-2">{{ ticker }}: {{ result.strategy.action }}</h2>
                    <p class="text-slate-400 italic">"{{ result.opinion }}"</p>
                    <div class="mt-4 flex flex-wrap gap-2">
                        <span class="bg-blue-900/40 text-blue-300 px-3 py-1 rounded-md text-xs">{{ result.strategy.horizon }}</span>
                        <span class="bg-slate-800 text-slate-300 px-3 py-1 rounded-md text-xs">Probabilidad: {{ result.strategy.probability }}%</span>
                    </div>
                </div>
            </div>

            <!-- Macro Context Card -->
            <div class="glass rounded-3xl p-8 card-hover">
                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                    <i data-lucide="globe" class="text-blue-400 w-5 h-5"></i> Contexto Macro
                </h3>
                <div class="space-y-4">
                    <div class="flex justify-between items-center">
                        <span class="text-slate-400 text-sm">Índice Miedo/Codicia</span>
                        <span class="font-medium">{{ result.macro.fear_greed_index }}/100</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-slate-400 text-sm">Volatilidad (VIX)</span>
                        <span class="font-medium">{{ result.macro.vix }}</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-slate-400 text-sm">Bonos 10Y (TNX)</span>
                        <span class="font-medium text-blue-400">{{ result.macro.tnx }}%</span>
                    </div>
                    <div class="p-3 bg-blue-500/10 rounded-xl mt-2">
                        <p class="text-xs text-blue-200">Entorno: {{ result.macro.tnx_trend }} con sentimiento {{ result.sentiment.label }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Pros & Cons -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="glass rounded-3xl p-8 border-l-4 border-emerald-500/50 card-hover">
                <h3 class="text-lg font-semibold mb-6 flex items-center gap-2 text-emerald-400">
                    <i data-lucide="check-circle" class="w-5 h-5"></i> Argumentos a Favor (Pros)
                </h3>
                <ul class="space-y-4">
                    {% for pro in result.strategy.pros %}
                    <li class="flex items-start gap-3">
                        <span class="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        <span class="text-sm text-slate-300">{{ pro }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            <div class="glass rounded-3xl p-8 border-l-4 border-rose-500/50 card-hover">
                <h3 class="text-lg font-semibold mb-6 flex items-center gap-2 text-rose-400">
                    <i data-lucide="alert-triangle" class="w-5 h-5"></i> Factores de Riesgo (Contras)
                </h3>
                <ul class="space-y-4">
                    {% for con in result.strategy.cons %}
                    <li class="flex items-start gap-3">
                        <span class="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                        <span class="text-sm text-slate-300">{{ con }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <!-- Technical & Fundamental Details -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <!-- Technical -->
            <div class="glass rounded-3xl p-6 card-hover">
                <h4 class="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Análisis Técnico</h4>
                <div class="space-y-3">
                    <div class="flex justify-between text-sm">
                        <span>RSI (14)</span>
                        <span class="{{ 'text-rose-400' if result.technical.rsi > 70 else 'text-emerald-400' if result.technical.rsi < 30 else 'text-white' }}">{{ result.technical.rsi }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span>Tendencia</span>
                        <span>{{ result.technical.trend }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span>MACD</span>
                        <span class="{{ 'text-emerald-400' if result.technical.macd == 'Bullish' else 'text-rose-400' }}">{{ result.technical.macd }}</span>
                    </div>
                </div>
            </div>

            <!-- Fundamental -->
            <div class="glass rounded-3xl p-6 card-hover">
                <h4 class="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Análisis Fundamental</h4>
                <div class="space-y-3">
                    <div class="flex justify-between text-sm">
                        <span>P/E Ratio</span>
                        <span>{{ result.fundamental.pe }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span>PEG Ratio</span>
                        <span>{{ result.fundamental.peg }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span>Analistas</span>
                        <span class="capitalize">{{ result.fundamental.recommendation }}</span>
                    </div>
                </div>
            </div>

            <!-- Key Levels -->
            <div class="glass rounded-3xl p-6 card-hover">
                <h4 class="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Niveles Clave</h4>
                <div class="space-y-3">
                    <div class="flex justify-between text-sm">
                        <span>Stop Loss</span>
                        <span class="text-rose-400 font-bold">{{ format_currency(result.strategy.stop_loss) if result.strategy.stop_loss else 'N/A' }}</span>
                    </div>
                    <div class="flex justify-between text-sm font-bold text-emerald-400">
                        <span>Obj. Corto</span>
                        <span>{{ format_currency(result.strategy.sell_levels.short_term) if result.strategy.sell_levels else 'N/A' }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span>Obj. Analistas</span>
                        <span>{{ format_currency(result.strategy.sell_levels.long_term) if result.strategy.sell_levels else 'N/A' }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alternatives -->
        <footer class="glass rounded-3xl p-6 text-center">
            <p class="text-xs text-slate-500 mb-2 uppercase tracking-tighter">Principales Alternativas en el Sector</p>
            <div class="flex justify-center gap-4">
                {% for alt in result.alternatives %}
                <span class="text-blue-400 font-bold hover:text-blue-300 cursor-pointer transition-colors">{{ alt }}</span>
                {% endfor %}
            </div>
            <p class="mt-6 text-[10px] text-slate-600 max-w-2xl mx-auto italic">
                Descargo de responsabilidad: Este reporte es generado por una Inteligencia Artificial con fines informativos únicamente. No constituye asesoría financiera. Realice su propia investigación antes de invertir.
            </p>
        </footer>
    </div>
    
    <script>
        lucide.createIcons();
    </script>
</body>
</html>
        """

    def generate(self, output_dir="reports"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Helper para formatear moneda
        def format_currency(value):
            if value is None: 
                return "N/A"
            try:
                val = float(value)
                return f"${val:,.2f}"
            except:
                return str(value)
        
        # Pre-procesar datos para evitar necesidad de filtros en template
        processed_result = self.result.copy()
        if isinstance(processed_result.get('price'), (int, float)):
            processed_result['price_formatted'] = format_currency(processed_result.get('price'))
        if isinstance(processed_result.get('strategy', {}).get('stop_loss'), (int, float)):
            processed_result['strategy'] = processed_result.get('strategy', {}).copy()
            processed_result['strategy']['stop_loss_formatted'] = format_currency(processed_result['strategy'].get('stop_loss'))
        
        template = Template(self._get_template())
        
        html_output = template.render(
            ticker=self.ticker,
            result=processed_result,
            timestamp=self.timestamp,
            confidence=abs(self.result['strategy']['confidence']),
            format_currency=format_currency  # Pasar como función disponible en template
        )
        
        filepath = os.path.join(output_dir, self.filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_output)
            
        return filepath
