from pathlib import Path


DATA_DIR = (Path(__file__).parent / "../../data").resolve()

from dotenv import load_dotenv
load_dotenv()