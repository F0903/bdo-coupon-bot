from datetime import date
from distutils.util import change_root
import sqlite3 as sql
from typing import Iterable


class ChannelsTable:
    def __init__(self, cursor: sql.Cursor):
        self.cursor = cursor
        self.ensure_table()

    def ensure_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS channels(
                guildID BIGINT PRIMARY KEY UNIQUE,
                channelID BIGINT UNIQUE
            )
            """
        )

    def add(self, guildID: int, channelID: int):
        self.cursor.execute(
            "INSERT OR REPLACE INTO channels VALUES (?, ?)", [guildID, channelID]
        )

    def remove(self, guildID: int):
        self.cursor.execute("DELETE FROM channels WHERE guildID=?", [guildID])

    def get(self, guildID: int) -> int:
        channel = self.cursor.execute(
            "SELECT channelID FROM channels WHERE guildID=?", [guildID]
        ).fetchone()[0]
        return channel

    def get_all(self) -> Iterable[int]:
        channels = map(
            lambda x: x[0],
            self.cursor.execute("SELECT channelID from channels").fetchall(),
        )
        return channels


class CouponCode:
    def __init__(self, hash: int, code: str, date: date):
        self.hash = hash
        self.code = (code,)
        self.date = date


class CouponCodesTable:
    def __init__(self, cursor: sql.Cursor):
        self.cursor = cursor
        self.ensure_table()

    def ensure_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS coupon_codes(
                hash BIGINT PRIMARY KEY UNIQUE
                code VARCHAR(18) UNIQUE
                date DATE
            )
            """
        )

    def add(self, hash: int, code: str, date: date):
        self.cursor.execute(
            "INSERT OR REPLACE INTO coupon_codes VALUES (?, ?, ?)", [hash, code, date]
        )

    def get(self, hash: int) -> CouponCode:
        code_info = self.cursor.execute(
            "SELECT * FROM coupon_codes WHERE hash=?", [hash]
        ).fetchone()
        code = CouponCode(hash, code_info[1], code_info[2])
        return code

    def get_all(self) -> Iterable[CouponCode]:
        channels = map(
            lambda x: CouponCode(x[0], x[1], x[2]),
            self.cursor.execute("SELECT * from coupon_codes").fetchall(),
        )
        return channels


class ScannerDb:
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def connect(self):
        self.db = sql.connect("../scanner.db")
        self.db.commit()

    def close(self):
        self.db.commit()
        self.db.close()

    def channels(self) -> ChannelsTable:
        return ChannelsTable(self.db.cursor())

    def coupons(self) -> CouponCodesTable:
        return CouponCodesTable(self.db.cursor())
