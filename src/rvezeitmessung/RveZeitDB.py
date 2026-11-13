#!/usr/bin/env python3
"""Database access for RVE Zeitmessung.

Created on 18.3.2023.
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import os
import sqlite3

from . import RveZeitConfig


class DB:
    """Class to handle database calls."""

    __dbConnection = None
    __dbCursor = None

    def __init__(self, config: RveZeitConfig):
        # Existenz feststellen
        sqlite_file = config.get("data.SQLiteFile")
        print(f"Initialize Database {sqlite_file}")
        if sqlite_file:
            if os.path.exists(sqlite_file):
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
            meta_x = self.__dbCursor.fetchone()[0]
            if meta_x is None:
                meta_x = 0

        print(f"MetaX: {meta_x}")
        return meta_x

    def get_max_number(self) -> int:
        """Highest number for default field 1."""
        max_number = 0
        if self.__dbCursor:
            sql = "SELECT MAX(nummer) FROM zeiten"
            self.__dbCursor.execute(sql)
            max_number = self.__dbCursor.fetchone()[0]
            if max_number is None:
                max_number = 0

        return max_number

    def get_data_by_number(self, nummer: str) -> int:
        """Get db entry by number."""
        row = None
        if self.__dbCursor and nummer is not None and nummer != "":
            sql = f"SELECT * FROM zeiten WHERE nummer = {nummer}"
            self.__dbCursor.execute(sql)
            row = self.__dbCursor.fetchone()
        return row

    def insert_data_by_number(
        self,
        nummer: str,
        timeString: str,
        hour: int,
        minuten: int,
        sekunden: int,
        secToday: int,
        backup1: int = 0,
        backup2: int = 0,
    ):
        """Create new zeiten entry."""
        if self.__dbCursor and nummer is not None and nummer != "":
            sql = (
                "INSERT INTO zeiten "
                + "(nummer, timeString, h, min, sec, secToday, backup1, backup2)"
                + f"VALUES( '{nummer}', '{timeString}', {hour}, {minuten}, {sekunden}, "
                + f"{secToday}, {backup1}, {backup2})"
            )
            # print(sql)
            self.__dbCursor.execute(sql)
            self.__dbConnection.commit()

    def update_data_by_number(
        self,
        nummer: str,
        timeString: str,
        hour: int,
        minuten: int,
        sekunden: int,
        secToday: int,
        backup1: int = 0,
        backup2: int = 0,
        oldSecToday: int = 0,
        comment: str = "New time for",
    ):
        """Update new zeiten entry."""
        if self.__dbCursor and nummer is not None and nummer != "":
            sql = (
                "UPDATE zeiten SET "
                + f"timeString = '{timeString}', "
                + f"h = {hour}, min = {minuten}, sec = {sekunden}, secToday = {secToday}"
                + f", backup1 = {backup1}, backup2 = {backup2} "
                + f"WHERE nummer = {nummer}"
            )
            # print(sql)
            self.__dbCursor.execute(sql)

            # -------------------------- M E T A   - Eintrag   --------
            sql = (
                "INSERT INTO meta "
                + "(timeString, h, min, sec, name, int, data) "
                + f"VALUES( '{timeString}', {hour}, {minuten}, {sekunden}, "
                + f"'{comment}', {nummer}, 'from {oldSecToday} to {timeString}')"
            )
            # print(sql)
            self.__dbCursor.execute(sql)
            self.__dbConnection.commit()

    def upsert_data_by_number(
        self,
        nummer: str,
        timeString: str,
        hour: int,
        minuten: int,
        sekunden: int,
        secToday: int,
        backup1: int = 0,
        backup2: int = 0,
    ):
        """Insert or update data entry depending if number already exists in database."""
        row = self.get_data_by_number(nummer)
        if row is None:
            self.insert_data_by_number(nummer, timeString, hour, minuten, sekunden, secToday)
        else:
            self.update_data_by_number(
                nummer,
                timeString,
                hour,
                minuten,
                sekunden,
                secToday,
                backup1=row[5],
                backup2=row[6],
                oldSecToday=row[1],
            )

    def delete_data_by_number(self, nummer: str):
        """Delete data entry from database."""
        if self.__dbCursor and nummer is not None and nummer != "":
            sql1 = f"delete from meta where int = {nummer!s}"
            sql2 = f"delete from zeiten where nummer =  {nummer!s}"
            self.__dbCursor.execute(sql1)
            self.__dbCursor.execute(sql2)
            self.__dbConnection.commit()

    def get_all_data(self) -> list:
        """Get alle zeiten einträge."""
        result = []
        if self.__dbCursor:
            sql = "SELECT * FROM zeiten ORDER BY secToday desc"
            self.__dbCursor.execute(sql)
            for satz in self.__dbCursor:
                result.append(satz)
        return result
