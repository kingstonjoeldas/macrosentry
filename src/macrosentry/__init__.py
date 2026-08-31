"""MacroSentry: Autonomous Fed/market surveillance with self-evaluating predictions."""
from dotenv import load_dotenv
load_dotenv()

__version__ = "0.1.0"

from .cli import main

__all__ = ["main"]
