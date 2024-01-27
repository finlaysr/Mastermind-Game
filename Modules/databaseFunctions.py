"""Finlay Robb - 20/11/23 - Functions for working with a SQLite Database"""
import sqlite3

class Database:
    def __init__(self, file: str):
        self.conn = sqlite3.connect(file)  # Connect to database or create new if it doesn't exist
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Create new tables if they do not already exist"""
        table_user = '''CREATE TABLE IF NOT EXISTS User (
        username TEXT (24) NOT NULL CHECK (LENGTH(username) >= 3) PRIMARY KEY,
        password TEXT (64) NOT NULL CHECK (LENGTH(password) >= 3) );'''

        table_score = '''CREATE TABLE IF NOT EXISTS Score (
        username   TEXT (24) NOT NULL REFERENCES User (username),
        mode       TEXT (10) NOT NULL CHECK (mode IN ('classic', 'timed', 'memory') ),
        difficulty TEXT (10) NOT NULL CHECK (difficulty IN ('easy', 'normal', 'hard', 'custom') ),
        score      INTEGER   NOT NULL CHECK (score > 0),
        date       TEXT (10) NOT NULL,
        time       TEXT (10) NOT NULL,
        PRIMARY KEY (username, date, time),
        FOREIGN KEY (username) REFERENCES User (username) );'''

        with self.conn:
            self.cursor.execute(table_user)
            self.cursor.execute(table_score)

    def add_user(self, username: str, password: str) -> None:
        """Add a new user to the User database"""
        # ? represents value to be added when executing
        command = '''INSERT INTO User(username, password) VALUES (?, ?);'''
        with self.conn:
            self.cursor.execute(command, (username, password))

    def add_score(self, username: str, mode: str, difficulty: str, score: int) -> None:
        """Add a new score to the score database"""
        command = '''INSERT INTO Score(username, mode, difficulty, score, date, time)
                        VALUES (?, ?, ?, ?, CURRENT_DATE, CURRENT_TIME);'''
        with self.conn:
            self.cursor.execute(command, (username, mode, difficulty, score))

    def select(self, query: str, params: list | set | tuple = ()) -> list:
        """Select data from database"""
        with self.conn:
            self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute(self, query: str, params: list | set | tuple = ()) -> None:
        """Execute a command on a database"""
        with self.conn:
            self.cursor.execute(query, params)

    def finish(self):
        """Close the connection to the database"""
        self.conn.close()
