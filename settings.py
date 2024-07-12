from pathlib import Path
import enum

BASE_BATH = Path(__file__).parent
TESTS_PATH = BASE_BATH / 'tests'

APP_PATH = BASE_BATH / 'app'
STATIC_PATH = APP_PATH / 'static'
TEMPLATES_PATH = APP_PATH / 'templates'

ALLOWED_REPORTERS = [
    "FRAN",
    "PAULA"
]

LOCALE = 'es_ES'

DEV_MODE = False
