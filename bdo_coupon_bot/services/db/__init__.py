import os

from .transaction import DATA_DIR, DatabaseTransaction

__all__ = ["DatabaseTransaction"]

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
