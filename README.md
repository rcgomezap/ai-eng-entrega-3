# AI Engineering Entrega 3

Pipeline de extraccion tecnica con LangChain, LCEL y salida estructurada validada con Pydantic. El proyecto toma texto tecnico, como logs de error o descripciones de arquitectura, y devuelve tecnologias detectadas, criticidad y un resumen tecnico.

## Requisitos

- Python 3.11+
- `uv`
- Credenciales para un proveedor compatible con `ChatOpenAI`

## Configuracion

Crea un archivo `.env` basado en `.env.example` y define las variables necesarias para tu proveedor.

Variables usadas por el proyecto:

- `OPENAI_API_KEY`: clave del proveedor compatible con OpenAI.
- `BASE_URL`: endpoint alternativo opcional, por ejemplo OpenRouter.
- `LLM_MODEL`: modelo a usar. Por defecto: `gpt-4o-mini`.

## Instalacion

```bash
uv sync
```

## Uso

Ejecutar el menu interactivo:

```bash
uv run python main.py
```

Ejecutar el ejemplo minimo:

```bash
uv run python example.py
```

Verificar tipos:

```bash
uv run pyright
```

## Arquitectura

- `schemas.py`: define los modelos Pydantic de entrada y salida.
- `clients.py`: contiene la abstraccion del cliente y la implementacion LCEL con ChatOpenAI.
- `chain.py`: expone una fachada simple para ejecutar el pipeline.
- `main.py`: menu CLI con manejo de errores orientado a usuario.
- `example.py`: script pequeno para probar el flujo completo.

Flujo principal:

```text
TechnicalExtractionInput -> TechnicalExtractionClient -> LCEL chain -> TechnicalExtraction
```

La cadena LCEL sigue la forma requerida:

```python
prompt | model.with_structured_output(TechnicalExtraction)
```

Luego se aplica `.with_retry()` y se valida la salida final con Pydantic.

## Salida Esperada

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "API con cache en Redis y persistencia en PostgreSQL; cuello de botella en conexiones concurrentes."
}
```

## Manejo De Errores

El proyecto separa fallos recuperables en categorias:

- Entrada invalida: el texto no cumple el esquema Pydantic esperado.
- Falla del proveedor: el modelo o endpoint falla luego de los reintentos.
- Salida invalida: la respuesta no cumple el esquema `TechnicalExtraction`.

El CLI captura estos errores y muestra mensajes concisos sin imprimir tracebacks al usuario.

## Logs

Los logs permiten observar:

- Inicio del proceso de extraccion.
- Cantidad maxima de reintentos configurada.
- Validacion exitosa de la salida.
- Fallos controlados del proveedor o validacion.

## Skill Del Proyecto

Este repositorio incluye un skill de OpenCode en:

```text
.opencode/skills/entrega-ai-eng/SKILL.md
```

El skill resume las reglas generales para este tipo de entregas: abstracciones, schemas Pydantic, LCEL, manejo de errores, logging, README y verificacion.

Despues de crear o modificar skills de OpenCode, reinicia OpenCode para que la sesion cargue la nueva configuracion.

## Troubleshooting

- Si falta una API key, revisa `.env` y las variables esperadas por tu proveedor.
- Si el proveedor falla, valida `BASE_URL`, `LLM_MODEL` y conectividad.
- Si `pyright` reporta tipos parcialmente desconocidos de LangChain, encapsula el borde con `Protocol` y `cast` en la implementacion del cliente.
- Si el modelo devuelve una salida incompleta, revisa el prompt, el schema y los logs de reintentos.
