from os import getenv
from dotenv import load_dotenv
from src.backend.agents.analyst.agent import mymain


if __name__ == "__main__":
    load_dotenv()
    print(getenv("MODEL_API_KEY"))
    mymain()
