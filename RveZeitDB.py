#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import RveZeitConfig
import os
import sys
import sqlite3

class DB:
    """
    Class to handle database calls
    """

    __dbConnection = None
    __dbCursor = None

    def __init__(self, config: RveZeitConfig):
        print(f"Initialize Database")
        # Existenz feststellen
        sqliteFile = config.get("data.SQLiteFile")
        if sqliteFile:
            if os.path.exists( sqliteFile ):
                # Verbindung zur Datenbank erzeugen
                self.__dbConnection = sqlite3.connect( sqliteFile )
                # Datensatzcursor erzeugen
                self.__dbCursor = self.__dbConnection.cursor()

                print("Datenbank war bereits vorhanden.")
            else:
                # Verbindung zur Datenbank erzeugen
                self.__dbConnection = sqlite3.connect( sqliteFile )
                # Datensatzcursor erzeugen
                self.__dbCursor = self.__dbConnection.cursor()

                # Tabellen erzeugen
                sql = "CREATE TABLE zeiten(" \
                  "nummer INTEGER PRIMARY KEY, " \
                  "timeString TEXT, " \
                  "h INTEGER, " \
                  "min INTEGER, " \
                  "sec INTEGER, " \
                  "secToday INTEGER, " \
                  "backup1 INTEGER, " \
                  "backup2 INTEGER)"
                self.__dbCursor.execute(sql)
                # ------------------------------------------
                sql = "CREATE TABLE meta(" \
                      "nummer INTEGER PRIMARY KEY AUTOINCREMENT, " \
                      "timeString TEXT, " \
                      "h INTEGER, " \
                      "min INTEGER, " \
                      "sec INTEGER, " \
                      "name TEXT, " \
                      "int INTEGER, " \
                      "data TEXT)"
                self.__dbCursor.execute(sql)
                self.__dbConnection.commit()
                # ------------------------------------------
                print("Datenbank wurde neu erstellt.")
        else:
            print("ERROR: No SQLiteFile specified in configuration.")

    
    def __del__(self):
        print(f"Close Database")
        # Verbindung beend
        if self.__dbConnection:
            self.__dbConnection.close()

    def getMaxMeta(self)-> int:
        """
        get index for Meta
        """
        metaX = 0
        if self.__dbCursor:
            sql = "SELECT MAX(nummer) FROM meta"
            self.__dbCursor.execute(sql)
            metaX = self.__dbCursor.fetchone()[0]
            if(metaX is None):
                metaX = 0
            
        print(f"MetaX: {metaX}")
        return metaX

    def getMaxNumber(self)-> int:
        """
        highest number for default field 1
        """
        maxNumber = 0
        if self.__dbCursor:
            sql = "SELECT MAX(nummer) FROM zeiten"
            self.__dbCursor.execute(sql)
            maxNumber = self.__dbCursor.fetchone()[0]
            if(maxNumber is None):
                maxNumber = 0

        return maxNumber

    def getDataByNumber(self, nummer:str)-> int:
        """
        get db entry by number
        """
        row = None
        if self.__dbCursor and nummer != None and nummer != "":
            sql=f"SELECT * FROM zeiten WHERE nummer = {nummer}"
            self.__dbCursor.execute(sql)
            row = self.__dbCursor.fetchone()
        return row
    
    def insertDataByNumber(self, nummer:str, timeString:str, hour:int, minuten:int, sekunden:int, secToday: int, backup1: int = 0, backup2: int = 0):
        """
        create new zeiten entry
        """
        if self.__dbCursor and nummer != None and nummer != "":
            sql = f"INSERT INTO zeiten " \
                + f"(nummer, timeString, h, min, sec, secToday, backup1, backup2)" \
                + f"VALUES( '{nummer}', '{timeString}', {hour}, {minuten}, {sekunden}, " \
                + f"{secToday}, {backup1}, {backup2})"
            #print(sql)
            self.__dbCursor.execute(sql)
            self.__dbConnection.commit()

    def updateDataByNumber(self, nummer:str, timeString:str, hour:int, minuten:int, sekunden:int, secToday: int, backup1: int = 0, 
                           backup2: int = 0, oldSecToday: int = 0, comment: str = "New time for"):
        """
        update new zeiten entry
        """
        if self.__dbCursor and nummer != None and nummer != "":
            sql = f"UPDATE zeiten SET " \
                + f"timeString = '{timeString}', " \
                + f"h = {hour}, min = {minuten}, sec = {sekunden}, secToday = {secToday}" \
                + f", backup1 = {backup1}, backup2 = {backup2} " \
                + f"WHERE nummer = {nummer}"
            #print(sql)
            self.__dbCursor.execute(sql)

            # -------------------------- M E T A   - Eintrag   --------
            sql = f"INSERT INTO meta " \
                + f"(timeString, h, min, sec, name, int, data) " \
                + f"VALUES( '{timeString}', {hour}, {minuten}, {sekunden}, " \
                + f"'{comment}', {nummer}, 'from {oldSecToday} to {timeString}')"
            #print(sql)
            self.__dbCursor.execute(sql)
            self.__dbConnection.commit()

    def upsertDataByNumber(self, nummer:str, timeString:str, hour:int, minuten:int, sekunden:int, secToday: int, backup1: int = 0, backup2: int = 0):
        """
        Insert or update data entry depending if number already exists in database.
        """
        row = self.getDataByNumber(nummer)
        if row is None:
            self.insertDataByNumber(nummer, timeString, hour, minuten, sekunden, secToday)
        else:
            self.updateDataByNumber(nummer, timeString, hour, minuten, sekunden, secToday, backup1=row[5], backup2=row[6], oldSecToday=row[1])

    def deleteDataByNumber(self, nummer:str):
        """
        Delete data entry from database
        """
        if self.__dbCursor and nummer != None and nummer != "":
            sql1 = f"delete from meta where int = {str(nummer)}"
            sql2 = f"delete from zeiten where nummer =  {str(nummer)}"
            self.__dbCursor.execute(sql1)
            self.__dbCursor.execute(sql2)
            self.__dbConnection.commit()



    def getAllData(self) -> list:
        """
        get alle zeiten einträge
        """
        result = []
        if self.__dbCursor:
            sql = "SELECT * FROM zeiten ORDER BY secToday desc"
            self.__dbCursor.execute(sql)
            for satz in self.__dbCursor:
                result.append(satz)
        
        return result