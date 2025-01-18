from pathlib import Path
from typing import Final

PROJECT_ID: Final[str] = "mlds-cap-2024-lexlead-advisor"
LOCATION_ID: Final[str] = "us-central1"

PROJECT_ROOT: Final[Path] = Path(__file__).parents[1]
CHROMA_VECTORS: Final[Path] = PROJECT_ROOT / "chroma_vector_store"
DOTENV_PATH: Final[Path] = PROJECT_ROOT / ".env"
