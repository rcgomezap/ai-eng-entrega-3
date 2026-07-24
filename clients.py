import logging
import os
from abc import ABC, abstractmethod
from typing import Protocol, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from schemas import TechnicalExtraction, TechnicalExtractionInput

logger = logging.getLogger(__name__)
MAX_RETRY_ATTEMPTS = 3


class SupportsStructuredOutput(Protocol):
    def with_structured_output(
        self,
        schema: type[TechnicalExtraction],
    ) -> Runnable[object, object]: ...


class TechnicalExtractionClient(ABC):
    @abstractmethod
    async def extract(self, input_data: BaseModel) -> TechnicalExtraction:
        pass


class LCELTechnicalExtractionClient(TechnicalExtractionClient):
    def __init__(self) -> None:
        model = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            base_url=os.getenv("BASE_URL"),
            temperature=0,
        )
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    "Eres un asistente experto en análisis técnico. Extrae las tecnologías "
                    "identificadas, determina el nivel de criticidad y genera un resumen "
                    "técnico conciso del texto provisto.\n"
                    "Usa nivel_de_criticidad='alta' para caídas, errores críticos, pérdida "
                    "de datos, cuellos de botella severos o incidentes de producción; "
                    "'media' para riesgos relevantes; y 'baja' para hallazgos menores."
                ),
            ),
            ("human", "Texto a analizar:\n{text}"),
        ])
        structured_model = cast(SupportsStructuredOutput, model).with_structured_output(
            TechnicalExtraction
        )
        self._chain: Runnable[dict[str, str], object] = cast(
            Runnable[dict[str, str], object],
            (prompt | structured_model).with_retry(
                stop_after_attempt=MAX_RETRY_ATTEMPTS,
            ),
        )

    async def extract(self, input_data: BaseModel) -> TechnicalExtraction:
        validated_input = TechnicalExtractionInput.model_validate(input_data)
        logger.info(
            "Iniciando extraccion tecnica estructurada con hasta %s intentos",
            MAX_RETRY_ATTEMPTS,
        )
        try:
            raw_result = await self._chain.ainvoke({"text": validated_input.text})
            result = TechnicalExtraction.model_validate(raw_result)
            logger.info(
                "Validacion completada: tecnologias=%s criticidad=%s",
                len(result.tecnologias),
                result.nivel_de_criticidad,
            )
            return result
        except Exception:
            logger.exception("Fallo la extraccion estructurada despues de los reintentos")
            raise
