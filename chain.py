from clients import LCELTechnicalExtractionClient, TechnicalExtractionClient
from schemas import TechnicalExtraction, TechnicalExtractionInput

default_client: TechnicalExtractionClient = LCELTechnicalExtractionClient()


async def process_text(input_data: TechnicalExtractionInput) -> TechnicalExtraction:
    return await default_client.extract(input_data)


def call_chain(text: str) -> TechnicalExtraction:
    import asyncio

    return asyncio.run(process_text(TechnicalExtractionInput(text=text)))
