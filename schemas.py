from typing import Literal

from pydantic import BaseModel, Field

CriticityLevel = Literal["baja", "media", "alta"]


class TechnicalExtractionInput(BaseModel):
    text: str = Field(description="Texto tecnico a analizar.", min_length=1)


class TechnicalExtraction(BaseModel):
    tecnologias: list[str] = Field(
        description="Tecnologias, frameworks, servicios, bases de datos o herramientas mencionadas."
    )
    nivel_de_criticidad: CriticityLevel = Field(
        description="Nivel de criticidad tecnica inferido: baja, media o alta."
    )
    resumen_tecnico: str = Field(
        description="Resumen tecnico conciso del problema, arquitectura o hallazgo principal."
    )
