import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from chain import process_text
from schemas import TechnicalExtractionInput


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    text = (
        "La API en FastAPI usa Redis como cache y PostgreSQL para persistencia. "
        "Se detecta cuello de botella en conexiones concurrentes y timeouts en produccion."
    )
    result = await process_text(TechnicalExtractionInput(text=text))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
