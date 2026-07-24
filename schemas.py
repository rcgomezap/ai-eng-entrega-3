from enum import Enum
from typing import List

from pydantic import BaseModel, Field

class CriticityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TechnicalEntityChainInput(BaseModel):
    input : str = Field(description="Entrada de texto para extraccion de entidades tecnicas")


class TechnicalEntityChainOutput(BaseModel):
    tecnologias : List[str] = Field(description="Tecnologias identificadas")
    nivel_de_criticidad : CriticityLevel = Field(description="Nivel de criticidad")
    resumen_tecnico : str = Field(description="Resumen tecnico")

