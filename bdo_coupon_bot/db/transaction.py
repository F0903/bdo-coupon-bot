import sqlite3 as sql
from .subscribers import SubscribersTable
from .coupons import CouponTable


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
        self.db = sql.connect("data.db")

    def close(self):
        self.db.commit()
        self.db.close()

    @property
    def subscribers(self) -> SubscribersTable:
        return self._subscribers

    @property
    def coupons(self) -> CouponTable:
        return self._coupons
