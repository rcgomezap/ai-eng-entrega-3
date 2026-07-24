import logging
import os
from abc import ABC, abstractmethod
from typing import Protocol, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from schemas import TechnicalExtraction, TechnicalExtractionInput

logger = logging.getLogger(__name__)
MAX_RETRY_ATTEMPTS = 3


class TechnicalExtractionError(Exception):
    """Base exception for recoverable extraction failures."""


class TechnicalExtractionInputError(TechnicalExtractionError):
    """Raised when the extraction input does not match the expected schema."""


class TechnicalExtractionProviderError(TechnicalExtractionError):
    """Raised when the LLM provider fails after retries."""


class TechnicalExtractionOutputError(TechnicalExtractionError):
    """Raised when the model response cannot be validated."""


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
        model_name = os.getenv("LLM_MODEL") or "gpt-4o-mini"
        base_url = os.getenv("BASE_URL") or None
        model = ChatOpenAI(
            model=model_name,
            base_url=base_url,
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
        try:
            validated_input = TechnicalExtractionInput.model_validate(input_data)
        except ValidationError as exc:
            logger.warning("Entrada invalida para extraccion tecnica: %s", exc)
            raise TechnicalExtractionInputError(
                "El texto de entrada no cumple con el esquema esperado."
            ) from exc

        logger.info(
            "Iniciando extraccion tecnica estructurada con hasta %s intentos",
            MAX_RETRY_ATTEMPTS,
        )

        try:
            raw_result = await self._chain.ainvoke({"text": validated_input.text})
        except Exception as exc:
            logger.error("Fallo la extraccion estructurada despues de los reintentos: %s", exc)
            logger.debug("Detalle del fallo del proveedor LLM", exc_info=True)
            raise TechnicalExtractionProviderError(
                "No se pudo obtener una respuesta valida del proveedor LLM."
            ) from exc

        try:
            result = TechnicalExtraction.model_validate(raw_result)
        except ValidationError as exc:
            logger.warning("Salida invalida del modelo: %s", exc)
            raise TechnicalExtractionOutputError(
                "La respuesta del modelo no cumple con el esquema TechnicalExtraction."
            ) from exc

        logger.info(
            "Validacion completada: tecnologias=%s criticidad=%s",
            len(result.tecnologias),
            result.nivel_de_criticidad,
        )
        return result
