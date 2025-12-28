import sys
sys.path.insert(0, '/Users/carlosfuentes/GitHub/spectral-galileo/src')
from spectral_galileo.core import agent
from colorama import Fore, Style

print("═" * 70)
print("🧪 DEMO: Análisis de Tendencia para Veredictos NEUTRAL/HOLD")
print("═" * 70)
print()

# Análisis real
print("Probando con ticker real (short-term para más probabilidad de NEUTRAL)...\n")

tickers_to_try = ['BA', 'DIS', 'INTC', 'F', 'AAL', 'DAL', 'LYFT']

for ticker in tickers_to_try:
    try:
        print(f"Analizando {ticker}...", end='', flush=True)
        trading_agent = agent.FinancialAgent(ticker, is_short_term=True, skip_external_data=True)
        result = trading_agent.run_analysis()
        
        if result:
            verdict = result['strategy']['verdict']
            confidence = result['strategy']['confidence']
            print(f" {verdict} (Confianza: {confidence:.1f}%)")
            
            if 'NEUTRAL' in verdict or 'HOLD' in verdict:
                print(f"\n✅ {ticker} dio {verdict} - Mostrando análisis completo:\n")
                report = trading_agent.get_report_string()
                
                # Imprimir la sección relevante
                lines = report.split('\n')
                in_trend_section = False
                for i, line in enumerate(lines):
                    if 'ANÁLISIS DE TENDENCIA' in line:
                        in_trend_section = True
                    
                    if in_trend_section:
                        print(line)
                        
                    if in_trend_section and 'POR QUÉ COMPRAR' in line:
                        break
                
                print("\n✅ Demo completado")
                break
    except Exception as e:
        print(f" Error: {str(e)}")
        continue
else:
    print("\n⚠️ Ningún ticker dio NEUTRAL - Todos los tickers están en tendencia definida")
    print("Esto es normal - cuando hay señales fuertes, no hay NEUTRAL")

print("\n" + "═" * 70)
print("💡 NOTA: La sección 'ANÁLISIS DE TENDENCIA' solo aparece cuando")
print("         el veredicto es NEUTRAL/HOLD, mostrando:")
print("         • Hacia dónde tiende (COMPRA o VENTA)")
print("         • Qué tan cerca está del umbral")
print("         • Visualización con barra de posición")
print("═" * 70)
