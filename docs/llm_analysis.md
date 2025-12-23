# Análisis con IA usando Gemini API

## 🤖 Descripción

El modo de análisis con IA utiliza **Gemini 2.0 Flash** de Google para realizar un análisis profundo y contextual de acciones, complementando el análisis tradicional basado en reglas.

### ¿Qué hace diferente?

**Análisis Tradicional (`python main.py TICKER`)**:
- ✅ Reglas fijas y umbrales predefinidos
- ✅ Scoring basado en 16 factores
- ✅ 100% determinista
- ✅ Gratis siempre
- ✅ Instantáneo

**Análisis con IA (`python main.py --ai TICKER`)**:
- 🤖 Análisis contextual y matizado
- 🤖 Comprensión profunda de noticias
- 🤖 Razonamiento similar a analista humano
- 🤖 Explicaciones detalladas
- 💰 Requiere API key (tier gratuito disponible)
- ⏱️ 2-5 segundos por análisis

---

## 🚀 Setup

### 1. Instalar Dependencias

```bash
pip install google-generativeai
```

### 2. Obtener API Key

1. Ve a [Google AI Studio](https://aistudio.google.com/apikey)
2. Crea un proyecto (si no tienes uno)
3. Genera una API key
4. Copia la key

### 3. Configurar API Key

**Opción 1: Variable de Entorno (Recomendado)**
```bash
export GEMINI_API_KEY="tu_api_key_aquí"
```

**Opción 2: Archivo .env**
```bash
# Crear archivo .env en el directorio del proyecto
echo "GEMINI_API_KEY=tu_api_key_aquí" > .env
```

---

## 📖 Uso

### Análisis Simple

```bash
python main.py --ai AAPL
```

### Comparar con Análisis Tradicional

```bash
# Análisis tradicional
python main.py AAPL

# Análisis con IA
python main.py --ai AAPL
```

---

## 💰 Precios de Gemini API

### Tier Gratuito (Google AI Studio)

| Modelo | Requests/Día | Requests/Min | Costo |
|--------|--------------|--------------|-------|
| Gemini 2.0 Flash | 1,500 | 15 | **GRATIS** |

**Límites del tier gratuito**:
- ✅ 1,500 requests por día (suficiente para ~200 análisis)
- ✅ 15 requests por minuto
- ✅ Sin tarjeta de crédito requerida
- ✅ Ideal para uso personal

### Tier de Pago (Vertex AI / Gemini API)

| Modelo | Input | Output | Costo por Análisis* |
|--------|-------|--------|---------------------|
| Gemini 2.0 Flash | $0.075/1M tokens | $0.30/1M tokens | ~$0.002 USD |
| Gemini 1.5 Pro | $1.25/1M tokens | $5.00/1M tokens | ~$0.03 USD |

\* *Estimado por análisis típico (~5,000 tokens)*

**Ejemplo de Costos Mensuales**:

```
Escenario: 10 análisis por día
- 10 × 30 días = 300 análisis/mes
- 300 × $0.002 = $0.60 USD/mes con Gemini Flash

Escenario: 50 análisis por día (uso intensivo)
- 50 × 30 días = 1,500 análisis/mes
- 1,500 × $0.002 = $3.00 USD/mes con Gemini Flash
```

---

## 📊 Comparación: IA vs Tradicional

| Aspecto | Tradicional | Con IA |
|---------|-------------|--------|
| **Velocidad** | Instantáneo | 2-5 segundos |
| **Costo** | $0 siempre | $0 (tier gratis) o ~$0.002/análisis |
| **Análisis de Noticias** | Keywords simples | Comprensión profunda del contexto |
| **Explicaciones** | Reglas fijas | Razonamiento natural |
| **Actualizable** | Requiere código | Aprende de nuevos patrones |
| **Consistencia** | 100% determinista | Puede variar ligeramente |
| **API Key** | No requerida | Requerida |

---

## 🎯 ¿Cuándo Usar Cada Uno?

### Usa Análisis Tradicional (`python main.py TICKER`) cuando:
- ✅ Quieres análisis instantáneo
- ✅ Estás scaneando muchas acciones (--scan)
- ✅ Prefieres resultados 100% consistentes
- ✅ No quieres configurar API keys

### Usa Análisis con IA (`python main.py --ai TICKER`) cuando:
- 🤖 Quieres análisis profundo de noticias específicas
- 🤖 Necesitas contexto y matices
- 🤖 Buscas explicaciones detalladas del razonamiento
- 🤖 Tienes API key configurada

### Recomendación
**Usa ambos**: El análisis tradicional para screening rápido, y el análisis con IA para profundizar en las acciones más prometedoras.

---

## ⚠️ Limitaciones

1. **Requiere API Key**: No funciona sin configurar `GEMINI_API_KEY`
2. **Rate Limits**: Tier gratuito limitado a 1,500 requests/día
3. **Latencia**: 2-5 segundos vs instantáneo del tradicional
4. **Variabilidad**: Respuestas pueden variar ligeramente entre ejecuciones
5. **No es Asesoría Financiera**: Como cualquier herramienta, usa como referencia, no como única fuente

---

## 🛠️ Troubleshooting

### Error: "GEMINI_API_KEY no configurada"
```bash
# Solución:
export GEMINI_API_KEY="tu_key_aquí"
```

### Error: "google-generativeai no está instalado"
```bash
# Solución:
pip install google-generativeai
```

### Error: "Rate limit exceeded"
**Causa**: Superaste el límite de 15 requests/minuto o 1,500/día

**Solución**:
- Espera unos minutos
- O actualiza a tier de pago
- O reduce la frecuencia de análisis

### La API Key no funciona
- Verifica que copiaste la key completa
- Asegúrate de que el proyecto en Google Cloud está activo
- Regenera la key si es necesario

---

## 📝 Ejemplo de Output

```
================================================================================
ANÁLISIS CON IA: AAPL
================================================================================

Precio Actual: $195.71
Sector: Technology
Industria: Consumer Electronics

────────────────────────────────────────────────────────────────────────────────
ANÁLISIS GENERADO POR GEMINI AI
────────────────────────────────────────────────────────────────────────────────

VEREDICTO: COMPRA
CONFIANZA: 75%
HORIZONTE: Largo Plazo

RAZONES PARA COMPRAR:
- Sólidos fundamentales con P/E razonable de 29.1
- Dividendo atractivo del 0.5% y crecimiento constante
- Noticias recientes muestran innovación continua en IA y Vision Pro
- Posición de liderazgo en el ecosistema Apple permanece intacta
- ROE excepcional del 147% demuestra eficiencia operativa

RAZONES DE PRECAUCIÓN:
- Precio cercano a máximos históricos, podría haber corrección
- Dependencia de iPhone para mayoría de ingresos
- Competencia creciente en mercado de smartphones

ANÁLISIS DE NOTICIAS:
Las noticias recientes muestran enfoque continuo en innovación (Apple Intelligence, 
Vision Pro) y expansión de servicios. No hay señales de alarma regulatorias o 
problemas operativos significativos.

NIVELES CLAVE:
Stop Loss Sugerido: $175.00
Objetivo Corto Plazo: $210.00
Objetivo Largo Plazo: $250.00

RESUMEN:
Apple mantiene su posición de fortaleza con sólidos fundamentales y un ecosistema 
difícil de replicar. Es una buena adición a portafolios de largo plazo, 
especialmente en correcciones.

================================================================================
Análisis completado con IA
================================================================================

⚠️  Este análisis fue generado por IA y no constituye asesoría financiera.
   Realiza tu propia investigación antes de invertir.
```

---

## 🔗 Enlaces Útiles

- [Google AI Studio](https://aistudio.google.com/) - Obtener API key gratis
- [Documentación Gemini API](https://ai.google.dev/docs) - Guías y referencias
- [Vertex AI Console](https://console.cloud.google.com/vertex-ai) - Tier de pago
- [Gemini Pricing](https://ai.google.dev/pricing) - Precios actualizados
