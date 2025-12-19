import os
import sqlite3 as sql

from .tables.coupons import CouponTable
from .tables.subscribers import SubscribersTable

DATA_DIR = "/data" if os.environ.get("DOCKER_MODE") == "1" else "./data"


class DatabaseTransaction:
    def __enter__(self):
        self.connect()
        cursor = self.db.cursor()
        self._subscribers = SubscribersTable(cursor)
        self._coupons = CouponTable(cursor)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def connect(self):
        self.db = sql.connect(f"{DATA_DIR}/data.db")

    def close(self):
        self.db.commit()
        self.db.close()

    @property
    def subscribers(self) -> SubscribersTable:
        return self._subscribers

    @property
    def coupons(self) -> CouponTable:
        return self._coupons
