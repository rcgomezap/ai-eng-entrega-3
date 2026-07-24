from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging

from chain import process_text
from schemas import TechnicalExtractionInput

EXAMPLE_TEXT = (
    "La API en FastAPI usa Redis como cache y PostgreSQL para persistencia. "
    "Durante picos de trafico aparecen errores por conexiones concurrentes y "
    "timeouts que degradan el servicio en produccion."
)


async def run_example() -> None:
    result = await process_text(TechnicalExtractionInput(text=EXAMPLE_TEXT))
    print("\nSalida validada")
    print(result.model_dump_json(indent=2))


async def analyze_custom_text() -> None:
    text = input("\nIngresa el texto tecnico a analizar: ").strip()
    if not text:
        print("No se ingreso texto.")
        return

    result = await process_text(TechnicalExtractionInput(text=text))
    print("\nSalida validada")
    print(result.model_dump_json(indent=2))


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

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
    asyncio.run(main())
