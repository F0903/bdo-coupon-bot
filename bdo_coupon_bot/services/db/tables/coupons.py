import sqlite3 as sql
from typing import Iterable

from bdo_coupon_scanner.coupon import Coupon


class CouponTable:
    def __init__(self, cursor: sql.Cursor):
        self.cursor = cursor
        self.ensure_table()

    def ensure_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS coupons(
                code VARCHAR(18) PRIMARY KEY NOT NULL UNIQUE,
                date DATE,
                url TEXT
            )
            """
        )

    def add(self, coupon: Coupon):
        self.cursor.execute(
            "INSERT OR REPLACE INTO coupons VALUES (?, ?, ?)",
            [coupon.code, coupon.date, coupon.origin_link],
        )

    def get_all(self) -> Iterable[Coupon]:
        coupons = map(
            lambda x: Coupon(x[0], x[1], x[2]),
            self.cursor.execute("SELECT * FROM coupons").fetchall(),
        )
        return coupons

    def count(self) -> int:
        return self.cursor.execute("SELECT COUNT(*) FROM subscribers").fetchone()
