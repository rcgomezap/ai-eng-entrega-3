from dotenv import load_dotenv
load_dotenv()


from chain import call_chain
from schemas import TechnicalEntityChainInput



def main():
    result = call_chain(TechnicalEntityChainInput(input="langchain and aws have crashed! oh no lol"))
    print(result)

if __name__ == "__main__":
    main()
