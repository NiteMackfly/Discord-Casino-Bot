import sqlite3
import random
from functools import wraps
from typing import Tuple, List
from time import sleep

Entry = Tuple[int, int, int]


class Economy:
    """A wrapper for the economy database"""

    def __init__(self):
        self.open()

    def open(self):
        """Initializes the database"""
        self.conn = sqlite3.connect("economy.db", timeout=30)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.cur = self.conn.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS economy (
            user_id INTEGER NOT NULL PRIMARY KEY,
            money INTEGER NOT NULL DEFAULT 0,
            credits INTEGER NOT NULL DEFAULT 0
        )"""
        )

        # Check if kidneys column exists, if not, add it
        if not self._check_kidneys_column_exists():
            self._add_kidneys_column()

    def close(self):
        """Safely closes the database"""
        if self.conn:
            self.conn.commit()
            self.cur.close()
            self.conn.close()

    def _commit(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 5
            delay = 0.1
            for i in range(retries):
                try:
                    result = func(self, *args, **kwargs)
                    self.conn.commit()
                    return result
                except sqlite3.OperationalError as e:
                    self.conn.rollback()
                    if "locked" in str(e):
                        sleep(delay)
                        delay *= 2
                    else:
                        raise
            raise sqlite3.OperationalError("Database is locked")

        return wrapper

    def get_entry(self, user_id: int) -> Tuple[int, int, int, int]:
        self.cur.execute(
            "SELECT user_id, money, credits, COALESCE(kidneys, 2) as kidneys FROM economy WHERE user_id=:user_id",
            {"user_id": user_id},
        )
        result = self.cur.fetchone()
        if result:
            return result
        return self.new_entry(user_id)

    @_commit
    def new_entry(self, user_id: int) -> Entry:
        try:
            self.cur.execute(
                "INSERT INTO economy(user_id, money, credits) VALUES(?,?,?)",
                (user_id, 0, 0),
            )
            return self.get_entry(user_id)
        except sqlite3.IntegrityError:
            return self.get_entry(user_id)

    @_commit
    def remove_entry(self, user_id: int) -> None:
        self.cur.execute(
            "DELETE FROM economy WHERE user_id=:user_id", {"user_id": user_id}
        )

    @_commit
    def set_money(self, user_id: int, money: int) -> Entry:
        self.cur.execute("UPDATE economy SET money=? WHERE user_id=?", (money, user_id))
        return self.get_entry(user_id)

    @_commit
    def set_credits(self, user_id: int, credits: int) -> Entry:
        self.cur.execute(
            "UPDATE economy SET credits=? WHERE user_id=?", (credits, user_id)
        )
        return self.get_entry(user_id)

    @_commit
    def add_money(self, user_id: int, money_to_add: int) -> Entry:
        money = self.get_entry(user_id)[1]
        total = money + money_to_add
        if total < 0:
            total = 0
        self.set_money(user_id, total)
        return self.get_entry(user_id)

    @_commit
    def add_credits(self, user_id: int, credits_to_add: int) -> Entry:
        credits = self.get_entry(user_id)[2]
        total = credits + credits_to_add
        if total < 0:
            total = 0
        self.set_credits(user_id, total)
        return self.get_entry(user_id)

    def random_entry(self) -> Entry:
        self.cur.execute("SELECT * FROM economy")
        return random.choice(self.cur.fetchall())

    def top_entries(self, n: int = 0) -> List[Entry]:
        self.cur.execute("SELECT * FROM economy ORDER BY money DESC")
        return self.cur.fetchmany(n) if n else self.cur.fetchall()

    def _check_kidneys_column_exists(self):
        self.cur.execute("PRAGMA table_info(economy)")
        columns = [column[1] for column in self.cur.fetchall()]
        return "kidneys" in columns

    @_commit
    def _add_kidneys_column(self):
        self.cur.execute(
            "ALTER TABLE economy ADD COLUMN kidneys INTEGER NOT NULL DEFAULT 2"
        )
        self.cur.execute("UPDATE economy SET kidneys = 2 WHERE kidneys IS NULL")

    @_commit
    def remove_kidney(self, user_id: int) -> Entry:
        entry = self.get_entry(user_id)
        if entry[3] > 0:
            new_kidney_count = entry[3] - 1
            self.set_kidneys(user_id, new_kidney_count)
            self.add_money(user_id, 10000)
        return self.get_entry(user_id)

    @_commit
    def set_kidneys(self, user_id: int, kidneys: int) -> Entry:
        self.cur.execute(
            "UPDATE economy SET kidneys=? WHERE user_id=?", (kidneys, user_id)
        )
        return self.get_entry(user_id)
