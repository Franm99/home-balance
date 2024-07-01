from pathlib import Path

BASE_BATH = Path(__file__).parent
TESTS_PATH = BASE_BATH / 'tests'

APP_PATH = BASE_BATH / 'app'
STATIC_PATH = APP_PATH / 'static'
TEMPLATES_PATH = APP_PATH / 'templates'

DEV_MODE = True