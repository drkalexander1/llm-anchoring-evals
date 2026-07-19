"""Shared paths and package markers."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROMPTS_DIR = ROOT / "prompts"
DEFAULT_ITEMS_PATH = DATA_DIR / "items.yaml"
DEFAULT_PRIOR_B_PATH = DATA_DIR / "prior_b.csv"
