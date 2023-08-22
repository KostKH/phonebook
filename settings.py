"""Модуль с настройками приложения."""
from pathlib import Path

BASE_DIR = Path(__file__).parent / 'database'
BASE_DIR.mkdir(exist_ok=True)

DB_NAME = BASE_DIR / 'phones.csv'
OUTPUT_LINE_NUMBER = 15
