"""Separate packaged resources from user documents and settings."""
import os
from pathlib import Path
import sys

RESOURCE_ROOT = Path(__file__).resolve().parent


def user_root():
    if getattr(sys, 'frozen', False):
        local = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        return local / 'SASISOPA' / 'Datos'
    return RESOURCE_ROOT
