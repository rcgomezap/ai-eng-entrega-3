import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from schemas import TechnicalEntityChainInput, TechnicalEntityChainOutput

# 1. Enforce JSON mode (Forces the model to return valid JSON)
model = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "gpt-4o-mini"), 
    base_url=os.getenv("BASE_URL"),
    model_kwargs={"response_format": {"type": "json_object"}}
)

parser = PydanticOutputParser(pydantic_object=TechnicalEntityChainOutput)

# 2. Strict instructions to avoid Markdown code blocks
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "Eres un asistente experto en análisis técnico. Extrae las tecnologías "
            "identificadas, determina el nivel de criticidad y genera un resumen "
            "técnico conciso del texto provisto.\n\n"
            "INSTRUCCIONES CRÍTICAS:\n"
            "- DEBES devolver ÚNICAMENTE JSON válido.\n"
            "- NO envuelvas la respuesta en bloques de código markdown (```json).\n"
            "- NO incluyas texto conversacional antes ni después del JSON.\n\n"
            "{format_instructions}"
        ),
    ),
    ("human", "{input}"),
]).partial(format_instructions=parser.get_format_instructions())

model_with_retries = model.with_retry(stop_after_attempt=3)

# 3. Use the standard parser (no extra packages needed)
chain = prompt | model_with_retries | parser

def call_chain(input_data: TechnicalEntityChainInput) -> TechnicalEntityChainOutput:
    result = chain.invoke({"input": input_data.input})
    return result