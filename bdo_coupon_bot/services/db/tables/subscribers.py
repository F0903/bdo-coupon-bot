import sqlite3 as sql
from typing import Iterable


class Subscriber:
    def __init__(self, guildID: int, channelID: int):
        self.guildID = guildID
        self.channelID = channelID


class SubscribersTable:
    def __init__(self, cursor: sql.Cursor):
        self.cursor = cursor
        self.ensure_table()

    def ensure_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subscribers(
                guildID BIGINT PRIMARY KEY NOT NULL UNIQUE,
                channelID BIGINT NOT NULL UNIQUE
            )
            """
        )

    def add(self, elem: Subscriber):
        self.cursor.execute(
            "INSERT OR REPLACE INTO subscribers VALUES (?, ?)",
            [elem.guildID, elem.channelID],
        )

    def remove(self, guildID: int):
        self.cursor.execute("DELETE FROM subscribers WHERE guildID=?", [guildID])

    def get(self, guildID: int) -> int | None:
        sub = self.cursor.execute(
            "SELECT channelID FROM subscribers WHERE guildID=?", [guildID]
        ).fetchone()
        return sub[0] if sub is not None else None

    def get_all(self) -> Iterable[Subscriber]:
        subs = map(
            lambda x: Subscriber(x[0], x[1]),
            self.cursor.execute("SELECT * FROM subscribers").fetchall(),
        )
        return subs

    def count(self) -> int:
        res = self.cursor.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
        return res
