#!/usr/bin/env python3
"""Database access for RVE Zeitmessung.

Created on 18.3.2023.
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import sqlite3
from pathlib import Path
from typing import Any

from .RveZeitConfig import Config


class DB:
    """Class to handle database calls."""

    __dbConnection: sqlite3.Connection | None = None
    __dbCursor: sqlite3.Cursor | None = None

    def __init__(self, config: Config):
        # Existenz feststellen
        sqlite_file = config.get("data.SQLiteFile")
        print(f"Initialize Database {sqlite_file}")
        if sqlite_file:
            if Path(sqlite_file).exists():
                # Verbindung zur Datenbank erzeugen
                self.__dbConnection = sqlite3.connect(sqlite_file)
                # Datensatzcursor erzeugen
                self.__dbCursor = self.__dbConnection.cursor()

                print("Datenbank war bereits vorhanden.")
            else:
                # Verbindung zur Datenbank erzeugen
                self.__dbConnection = sqlite3.connect(sqlite_file)
                # Datensatzcursor erzeugen
                self.__dbCursor = self.__dbConnection.cursor()

                # Tabellen erzeugen
                sql = (
                    "CREATE TABLE zeiten("
                    "nummer INTEGER PRIMARY KEY, "
                    "timeString TEXT, "
                    "h INTEGER, "
                    "min INTEGER, "
                    "sec INTEGER, "
                    "secToday INTEGER, "
                    "backup1 INTEGER, "
                    "backup2 INTEGER)"
                )
                self.__dbCursor.execute(sql)
                # ------------------------------------------
                sql = (
                    "CREATE TABLE meta("
                    "nummer INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "timeString TEXT, "
                    "h INTEGER, "
                    "min INTEGER, "
                    "sec INTEGER, "
                    "name TEXT, "
                    "int INTEGER, "
                    "data TEXT)"
                )
                self.__dbCursor.execute(sql)
                self.__dbConnection.commit()
                # ------------------------------------------
                print("Datenbank wurde neu erstellt.")
        else:
            print("ERROR: No SQLiteFile specified in configuration.")

    def __del__(self):
        """Close the database connection when the object is destroyed."""
        print("Close Database")
        # Verbindung beend
        if self.__dbConnection:
            self.__dbConnection.close()

    def get_max_meta(self) -> int:
        """Get index for Meta."""
        meta_x = 0
        if self.__dbCursor:
            sql = "SELECT MAX(nummer) FROM meta"
            self.__dbCursor.execute(sql)
            result = self.__dbCursor.fetchone()[0]
            if result is not None:
                meta_x = int(result)

        print(f"MetaX: {meta_x}")
        return meta_x

    def get_max_number(self) -> int:
        """Highest number for default field 1."""
        max_number = 0
        if self.__dbCursor:
            sql = "SELECT MAX(nummer) FROM zeiten"
            self.__dbCursor.execute(sql)
            result = self.__dbCursor.fetchone()[0]
            if result is None:
                max_number = int(result)

        return max_number

    def get_data_by_number(self, nummer: int) -> tuple[Any, ...] | None:
        """Get db entry by number."""
        row = None
        if self.__dbCursor:
            sql = f"SELECT * FROM zeiten WHERE nummer = {nummer}"
            self.__dbCursor.execute(sql)
            row = self.__dbCursor.fetchone()
        return row

    def insert_data_by_number(
        self,
        number: int,
        time_string: str,
        hour: int,
        minuten: int,
        sekunden: int,
        sec_today: int,
        backup1: int = 0,
        backup2: int = 0,
    ):
        """Create new zeiten entry."""
        if self.__dbCursor and self.__dbConnection:
            sql = (
                "INSERT INTO zeiten "
                + "(nummer, timeString, h, min, sec, secToday, backup1, backup2)"
                + f"VALUES( '{number}', '{time_string}', {hour}, {minuten}, {sekunden}, "
                + f"{sec_today}, {backup1}, {backup2})"
            )
            # print(sql)
            self.__dbCursor.execute(sql)
            self.__dbConnection.commit()

    def update_data_by_number(
        self,
        nummer: int,
        time_string: str,
        hour: int,
        minuten: int,
        sekunden: int,
        sec_today: int,
        backup1: int = 0,
        backup2: int = 0,
        old_sec_today: int = 0,
        comment: str = "New time for",
    ):
        """Update new zeiten entry."""
        if self.__dbCursor and self.__dbConnection:
            sql = (
                "UPDATE zeiten SET "
                + f"timeString = '{time_string}', "
                + f"h = {hour}, min = {minuten}, sec = {sekunden}, secToday = {sec_today}"
                + f", backup1 = {backup1}, backup2 = {backup2} "
                + f"WHERE nummer = {nummer}"
            )
            # print(sql)
            self.__dbCursor.execute(sql)

            # -------------------------- M E T A   - Eintrag   --------
            sql = (
                "INSERT INTO meta "
                + "(timeString, h, min, sec, name, int, data) "
                + f"VALUES( '{time_string}', {hour}, {minuten}, {sekunden}, "
                + f"'{comment}', {nummer}, 'from {old_sec_today} to {time_string}')"
            )
            # print(sql)
            self.__dbCursor.execute(sql)
            self.__dbConnection.commit()

    def upsert_data_by_number(
        self,
        nummer: int,
        time_string: str,
        hour: int,
        minuten: int,
        sekunden: int,
        sec_today: int,
        backup1: int = 0,
        backup2: int = 0,
    ):
        """Insert or update data entry depending if number already exists in database."""
        row = self.get_data_by_number(nummer)
        if row is None:
            self.insert_data_by_number(nummer, time_string, hour, minuten, sekunden, sec_today)
        else:
            self.update_data_by_number(
                nummer,
                time_string,
                hour,
                minuten,
                sekunden,
                sec_today,
                backup1=row[5],
                backup2=row[6],
                old_sec_today=row[1],
            )

    def delete_data_by_number(self, nummer: int):
        """Delete data entry from database."""
        if self.__dbCursor and self.__dbConnection:
            sql1 = f"delete from meta where int = {nummer!s}"
            sql2 = f"delete from zeiten where nummer =  {nummer!s}"
            self.__dbCursor.execute(sql1)
            self.__dbCursor.execute(sql2)
            self.__dbConnection.commit()

    def get_all_data(self) -> list[Any]:
        """Get all time entries."""
        result = []
        if self.__dbCursor:
            sql = "SELECT * FROM zeiten ORDER BY secToday desc"
            self.__dbCursor.execute(sql)
            for entry in self.__dbCursor:
                result.append(entry)
        return result
