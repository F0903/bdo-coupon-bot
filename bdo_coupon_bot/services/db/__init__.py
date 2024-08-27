import os
from .transaction import DatabaseTransaction, DATA_DIR

__all__ = ["DatabaseTransaction"]

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
