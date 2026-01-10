#!/usr/bin/env python3
"""
Test simple de la función de acumulación sin dependencias complejas
"""

def calculate_combined_confidence(short_conf, long_conf):
    """Calcula confianza combinada (60% corto plazo + 40% largo plazo)."""
    combined = (short_conf * 0.6) + (long_conf * 0.4)
    return combined, short_conf, long_conf

def test_accumulation():
    """Test simple"""
    print("=" * 60)
    print("PRUEBA DE FUNCIÓN DE ACUMULACIÓN")
    print("=" * 60)
    
    # Escenarios de prueba
    scenarios = [
        ("Bullish Corto, Bearish Largo", 85, 30),
        ("Bullish Corto, Bullish Largo", 90, 85),
        ("Neutral Corto, Bullish Largo", 50, 80),
        ("Bearish Corto, Bearish Largo", 25, 20),
    ]
    
    for nombre, short, long in scenarios:
        combined, sc, lc = calculate_combined_confidence(short, long)
        print(f"\n{nombre}:")
        print(f"  Corto:    {sc:.0f}%")
        print(f"  Largo:    {lc:.0f}%")
        print(f"  Combinada (60% corto + 40% largo): {combined:.0f}%")
        
        # Determinar acción basada en combinada
        if combined >= 70:
            accion = "🟢 ACUMULAR AGRESIVA"
        elif combined >= 60:
            accion = "🟡 DCA (ACUMULAR GRADUAL)"
        elif combined >= 40:
            accion = "⚪ MANTENER (ESPERAR SEÑAL)"
        else:
            accion = "🔴 NO ACUMULAR"
        
        print(f"  Acción:   {accion}")
    
    print("\n" + "=" * 60)
    print("\nLEYENDA DE COLUMNAS:")
    print("  Corto Plazo (60%):    Momentum de 1-3 meses (timing)")
    print("  Largo Plazo (40%):    Fundamentales de 3-5 años (valor)")
    print("  Combinada:           Recomendación ponderada")
    print("\nRATING DE ACCIÓN:")
    print("  >= 70%:  ACUMULAR AGRESIVA   (Valor + Momentum)")
    print("  60-70%:  DCA (ACUMULAR GRADUAL) (Valor ok, Momentum débil)")
    print("  40-60%:  MANTENER/ESPERAR     (Neutral, sin señal clara)")
    print("  < 40%:   NO ACUMULAR         (Valor o Momentum malos)")
    print("=" * 60)

if __name__ == "__main__":
    test_accumulation()
