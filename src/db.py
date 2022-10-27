from datetime import date
import sqlite3 as sql
from typing import Iterable


class CouponCode:
    def __init__(self, hash: int, code: str, date: date):
        self.hash = hash
        self.code = code
        self.date = date


class CouponCodesTable:
    def __init__(self, cursor: sql.Cursor):
        self.cursor = cursor
        self.ensure_table()

    def ensure_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS coupon_codes(
                hash BIGINT PRIMARY KEY UNIQUE,
                code VARCHAR(18) UNIQUE,
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


class ChannelElement:
    def __init__(self, guildID: int, channelID: int):
        self.guildID = guildID
        self.channelID = channelID


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

    def add(self, elem: ChannelElement):
        self.cursor.execute(
            "INSERT OR REPLACE INTO channels VALUES (?, ?)",
            [elem.guildID, elem.channelID],
        )

    def remove(self, guildID: int):
        self.cursor.execute("DELETE FROM channels WHERE guildID=?", [guildID])

    def get(self, guildID: int) -> int:
        channel = self.cursor.execute(
            "SELECT channelID FROM channels WHERE guildID=?", [guildID]
        ).fetchone()[0]
        return channel

    def get_all(self) -> Iterable[ChannelElement]:
        channels = map(
            lambda x: ChannelElement(x[0], x[1]),
            self.cursor.execute("SELECT * from channels").fetchall(),
        )
        return channels


# TODO: VERY IMPORTANT: Prevent SQL injection
class ScannerDb:
    def __enter__(self):
        self.connect()
        cursor = self.db.cursor()
        self._channels = ChannelsTable(cursor)
        self._coupons = CouponCodesTable(cursor)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def connect(self):
        self.db = sql.connect("../scanner.db")

    def close(self):
        self.db.commit()
        self.db.close()

    @property
    def channels(self) -> ChannelsTable:
        return self._channels

    @property
    def coupons(self) -> CouponCodesTable:
        return self._coupons
