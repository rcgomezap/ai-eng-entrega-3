from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging

from clients import TechnicalExtractionError
from chain import process_text
from schemas import TechnicalExtractionInput

EXAMPLE_TEXT = (
    "La API en FastAPI usa Redis como cache y PostgreSQL para persistencia. "
    "Durante picos de trafico aparecen errores por conexiones concurrentes y "
    "timeouts que degradan el servicio en produccion."
)


async def run_example() -> None:
    await print_extraction(TechnicalExtractionInput(text=EXAMPLE_TEXT))


async def print_extraction(input_data: TechnicalExtractionInput) -> None:
    try:
        result = await process_text(input_data)
    except TechnicalExtractionError as exc:
        logging.getLogger(__name__).error("No se pudo completar la extraccion: %s", exc)
        print(f"\nError: {exc}")
        return

    print("\nSalida validada")
    print(result.model_dump_json(indent=2))


async def analyze_custom_text() -> None:
    text = input("\nIngresa el texto tecnico a analizar: ").strip()
    if not text:
        print("No se ingreso texto.")
        return

    await print_extraction(TechnicalExtractionInput(text=text))


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    while True:
        print("\nMenu principal")
        print("1. Ejecutar ejemplo del pipeline")
        print("2. Analizar texto personalizado")
        print("0. Salir")

        option = input("Selecciona una opcion: ").strip()
        if option == "1":
            await run_example()
        elif option == "2":
            await analyze_custom_text()
        elif option == "0":
            print("Hasta luego.")
            return
        else:
            print("Opcion invalida. Intenta de nuevo.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario.")
