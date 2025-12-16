# fx-conversor · BFSI – Energy & Resources

Aplicación de demo que muestra cómo un agente en Python decide de forma dinámica cuándo llamar a herramientas externas (tools) para responder preguntas en lenguaje natural en el contexto BFSI del sector de energía y recursos.

## Cómo Ejecutar
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `python app.py`

## Contexto y Motivación

En proyectos de energía (renovable o tradicional) es frecuente que:

- Los ingresos estén en moneda local (por ejemplo COP).
- La deuda y los contratos de suministro estén en USD o EUR.
- Las variaciones en la tasa de cambio afecten directamente el flujo de caja, la capacidad de pago y la rentabilidad.

Esta aplicación demuestra cómo un agente inteligente puede ayudar a equipos financieros a:

- **Convertir montos entre monedas** en tiempo real (USD, EUR, COP, etc.) usando una herramienta de API.
- **Responder preguntas conceptuales** sobre tasas de cambio, riesgo cambiario y su impacto en operaciones del sector energético usando un modelo de lenguaje (LLM).

## Arquitectura de la Solución

### Componentes Principales

#### 1. Tool de Tipos de Cambio (`src/fx_provider.py`)

- **Cliente FX**: Integración con la API pública de **Frankfurter** para consultar tasas de cambio en tiempo real.
- **Método**: `convert(amount: float, from_currency: str, to_currency: str) -> float`
- **Propósito**: Proporcionar tasas actualizadas para conversiones de moneda.

#### 2. Parser de Lenguaje Natural (`src/currency_agent.py` - clase `Parser`)

- **Función**: Analiza preguntas en español para detectar:
  - Monto a convertir
  - Moneda origen
  - Moneda destino
- **Lógica**: Búsqueda de palabras clave, números y códigos ISO de monedas.
- **Salida**: Tupla `(monto, moneda_origen, moneda_destino)` o `None` si no es una pregunta de conversión.

#### 3. Agente Orquestador (`src/currency_agent.py` - clase `CurrencyAgent`)

- **Flujo de decisión**:
  1. Recibe pregunta en español.
  2. Usa el `Parser` para intentar extraer datos de conversión.
  3. Si extrae montos y monedas → **Llama a la tool de FX** y retorna resultado numérico con badge "Usó tool de FX".
  4. Si no extrae datos → **Delega al LLM de Groq** para generar respuesta conceptual con badge "Respuesta solo LLM".

#### 4. Cliente LLM (`src/llm_client.py`)

- **Proveedor**: API de **Groq** con modelo `llama-3.1-8b-instant`.
- **System Prompt**: Analista financiero BFSI con experiencia en energía/recursos.
- **Parámetros**:
  - `temperature=0.3` (respuestas determinísticas)
  - `max_tokens=250` (respuestas breves, 3–6 frases)
- **Propósito**: Responder preguntas que no son de conversión con enfoque sectorial.

#### 5. Interfaz Web (`app.py` + `templates/index.html`)

- **Framework**: Flask + Bootstrap.
- **Características**:
  - Área de texto para preguntas libres.
  - 3 botones con preguntas predefinidas de demo.
  - Indicador visual (badge) que muestra si se usó tool o LLM.
  - Información del tipo de cambio de referencia (cuando aplica).

## Flujo de Funcionamiento

```
Usuario ingresa pregunta
           ↓
    Parser analiza
           ↓
    ¿Detectó conversión?
       /          \
      SÍ           NO
     /              \
  Llamar         Llamar
  Tool FX        LLM
    ↓              ↓
Retorna         Retorna
número      explicación
    ↓              ↓
    └────┬─────────┘
         ↓
      Respuesta con badge
```

## Preguntas de Demo

La interfaz incluye tres preguntas predefinidas para demostración:

### Pregunta 1 (Tool FX)
**Texto**: `¿Cuál es el valor de 100000 COP en USD hoy?`  
**Comportamiento**: 
- Parser extrae: 100000 COP → USD
- Llama a tool de FX
- Retorna: "100.000,00 COP equivalen aproximadamente a X,XX USD (tasa de referencia: 1 COP ≈ ... USD)."
- Badge: ✅ **Usó tool de FX**

### Pregunta 2 (Tool FX)
**Texto**: `¿Cuánto equivalen 500 EUR en COP con la tasa actual?`  
**Comportamiento**:
- Parser extrae: 500 EUR → COP
- Llama a tool de FX
- Retorna: "500,00 EUR equivalen aproximadamente a X.XXX,XX COP (tasa de referencia: 1 EUR ≈ ... COP)."
- Badge: ✅ **Usó tool de FX**

### Pregunta 3 (LLM)
**Texto**: `¿Qué significa tasa de cambio y por qué es importante en transacciones internacionales?`  
**Comportamiento**:
- Parser no extrae datos de conversión
- Delega a Groq
- Retorna: Explicación en 3–6 frases sobre tasa de cambio, con enfoque en energía/BFSI
- Badge: 📋 **Respuesta solo LLM**

## Cómo Ejecutar la Aplicación

### Prerequisitos

- Python 3.8+
- GitHub Codespaces (recomendado) o entorno Linux local
- API key de Groq (obtenerla en https://console.groq.com)

### Pasos de Instalación y Ejecución

#### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/fx-conversor.git
cd fx-conversor
```

#### 2. Crear y activar entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- `flask` – servidor web
- `requests` – cliente HTTP para APIs
- `groq` – cliente oficial de Groq API

#### 4. Configurar la API key de Groq

**En GitHub Codespaces** (recomendado):
- Ve a tu repositorio en GitHub.
- Settings → Secrets and variables → Codespaces.
- Crea un nuevo secret:
  - **Name**: `GROQ_API_KEY`
  - **Value**: Tu API key de Groq (obtener en https://console.groq.com/keys)
- Guarda.

La clave se inyecta automáticamente en el Codespace.

**En local** (desarrollo):
```bash
export GROQ_API_KEY="tu_api_key_aqui"
```

#### 5. Ejecutar la aplicación

```bash
python3 app.py
```

Verás:
```
 * Running on http://127.0.0.1:5000
```

En Codespaces, haz **Ctrl+click** sobre la URL o usa el botón "Abrir en navegador".

#### 6. Probar en el navegador

- Abre `http://127.0.0.1:5000`
- Escribe una pregunta en el área de texto **O** usa los botones de demo
- La aplicación muestra:
  - Respuesta con badge ("Usó tool de FX" o "Respuesta solo LLM")
  - Información del tipo de cambio (si aplica)

## Estructura del Proyecto

```
fx-conversor/
├── src/
│   ├── fx_provider.py       # Cliente API Frankfurter (tool de FX)
│   ├── currency_agent.py    # Parser + Agente orquestador
│   └── llm_client.py        # Cliente Groq (LLM)
├── templates/
│   └── index.html           # Interfaz web
├── app.py                   # Servidor Flask
├── requirements.txt         # Dependencias Python
├── README.md                # Este archivo
└── devcontainer.json        # Configuración Codespaces (opcional)
```

## Detalles Técnicos

### Decisión Tool vs LLM

El agente usa una estrategia de **decisión determinística**:

1. **Si el parser extrae datos de conversión válidos** → Usa la tool de FX.
2. **Si el parser retorna `None`** → Delega al LLM.

**Ventajas**:
- Respuestas numéricas precisas y actualizadas para conversiones.
- Explicaciones conceptuales ricas para preguntas abiertas.
- Control claro sobre cuándo usar cada recurso.

### Limitaciones y Notas

- Las tasas de cambio son de referencia (Frankfurter). No son tasas de banco ni traders; usan referencias de mercado real pero con latencia de minutos.
- El parser funciona bien para preguntas típicas; frases muy distintas pueden no interpretarse correctamente.
- El LLM usa `temperature=0.3` para ser determinístico; temperaturas mayores generarían más variabilidad.
- No hay historial de conversación; cada pregunta es independiente.

### Integración con Groq

- **Modelo**: `llama-3.1-8b-instant` (rápido, eficiente)
- **Latencia**: Típicamente < 1 segundo
- **Costo**: Groq ofrece plan gratuito con cuota mensual generosa

## Alineación con Requerimientos de la Actividad

Este proyecto demuestra:

✅ **Uso de dos tools**: 
- Tool 1: API Frankfurter (conversión de monedas)
- Tool 2: Modelo de IA (Groq LLM)

✅ **Decisión dinámica de tool**: El agente decide qué tool usar según el tipo de pregunta.

✅ **Contexto BFSI**: Aplicación en sector energía/recursos con enfoque en riesgo cambiario.

✅ **Interfaz clara**: UI que indica qué tool se utilizó.

✅ **Funcionamiento en Codespaces**: Configuración con secrets para producción.

## Proceso Iterativo de Desarrollo

### Fase 1: Fundación
- Implementación de `FrankfurterProvider` (cliente FX).
- Creación del `Parser` para extraer montos y monedas.
- Servidor Flask básico con formulario.

### Fase 2: Orquestación
- Desarrollo de `CurrencyAgent` como coordinador.
- Lógica de decisión: conversión vs. conceptual.
- Integración con interfaz web.

### Fase 3: LLM
- Integración con Groq (`llm_client.py`).
- Ajuste del system prompt para BFSI–energía.
- Parámetros optimizados para respuestas breves y directas.

### Fase 4: UX Mejorada
- Adición de badges informativos ("Usó tool de FX" / "Respuesta solo LLM").
- Botones de demo preconfigurados.
- Visualización del tipo de cambio de referencia.

### Fase 5: Producción
- Configuración de secrets en GitHub Codespaces.
- `requirements.txt` actualizado con todas las dependencias.
- README documentación completa.

## Cómo Extender la Aplicación

### Agregar más monedas
Simplemente usa códigos ISO válidos (EUR, GBP, JPY, etc.). La API de Frankfurter soporta ~170 monedas.

### Cambiar el modelo de LLM
En `src/llm_client.py`, reemplaza `model="llama-3.1-8b-instant"` por otro disponible en Groq (ej: `mixtral-8x7b-32768`).

### Mejorar el parser
Añade patrones regex más sofisticados o integra un NER (Named Entity Recognition) para detectar entidades financieras.

### Agregar historial
Usa sesiones de Flask o base de datos para guardar conversación.

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `GROQ_API_KEY not found` | Verifica que el secret está configurado en GitHub Codespaces (Settings → Secrets). |
| Pregunta de conversión devuelve "0,00" | Verifica que el parser extrae montos correctamente; ajusta el texto de la pregunta. |
| Error de conexión a Frankfurter | Revisa conectividad de red; la API de Frankfurter requiere acceso a internet. |
| LLM devuelve respuesta larga | Baja `max_tokens` en `src/llm_client.py` o ajusta el system prompt. |

## Licencia

Este proyecto es una demo educativa. Libre para usar y modificar con fines académicos.

## Contacto y Preguntas

Para consultas sobre la arquitectura, el uso de tools o la integración con Groq, revisa el documento técnico incluido en la entrega.
