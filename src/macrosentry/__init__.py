"""MacroSentry: Autonomous Fed/market surveillance with self-evaluating predictions."""
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

__version__ = "0.1.0"

from .cli import main

__all__ = ["main"]
