__version__ = "0.1.0"

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'apps'))
sys.path.insert(0, str(BASE_DIR / 'modules'))
sys.path.insert(0, str(BASE_DIR / 'components'))

from .celery import app as celery_app

__all__ = ('celery_app',)
