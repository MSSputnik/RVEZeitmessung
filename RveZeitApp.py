#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import RveZeitConfig
import RveZeitUI
import RveZeitDB
import RveZeitFtp

import time
import math
import tkinter as tk
from tkinter import messagebox, ttk


class App:
    """
    This class contains the actual application code
    """
    __config:RveZeitConfig = None
    __ui:RveZeitUI = None
    __changeNr = None
    __transport = None
    __styles = {}

    def __init__(self, config: RveZeitConfig, ui:RveZeitUI, db:RveZeitDB, transport:RveZeitFtp):
        """
        No idea what will be done here.
        """
        self.__config = config
        self.__ui = ui
        self.__db = db
        self.__transport = transport

        maxNumber = db.getMaxNumber()

        # Create Styles
        green = '#109410'
        red = '#ba1c1c'
        ttk.Style().configure('green.TButton', foreground=green)
        ttk.Style().configure('red.TButton', foreground=red)
        ttk.Style().configure('green.TEntry', foreground=green)
        ttk.Style().configure('red.TEntry', foreground=red)

        self.__styles = {
            "defaultButton" : 'TButton',
            "greenButton" : 'green.TButton',
            "redButton" : 'red.TButton',
            "defaultEntry" : 'TEntry',
            "greenEntry" : 'green.TEntry',
            "redEntry" : 'red.TEntry'
        }


        # activate scrollbar in listbox
        scrollbar=ui.getWidget("window.frmEntryList.frmEntryListScrollbar")
        listbox=ui.getWidget("window.frmEntryList.frmEntryListBox")
        if listbox and scrollbar:
            listbox.config(yscrollcommand = scrollbar.set)
            scrollbar.config(command = listbox.yview )

        # activate buttons etc
        ui.insert("window.text1", 0, str(maxNumber+1))
        ui.config("window.btnCheck1", command=self.check_1)
        ui.config("window.btnCommit1", command=self.zeitOf1)
        ui.config("window.btnCheck2", command=self.check_2)
        ui.config("window.btnCommit2", command=self.zeitOf2)
        ui.config("window.btnCheck3", command=self.check_3)
        ui.config("window.btnCommit3", command=self.zeitOf3)
        ui.config("window.btnUpdateList", command=self.refeshList)
        ui.config("window.btnChangeGet", command=self.get4Modification)
        ui.config("window.btnChangeSave", command=self.changeTime)
        ui.config("window.btnChangeDelete", command=self.deleteTime)
        ui.config("window.btnSaveLocal", command=self.writeLocalTrzFile)
        ui.config("window.btnTransfere", command=self.sendFile)

        # activate key actions
        ui.bind("window", "s", lambda event:self.zeitOf1())
        ui.bind("window", "d", lambda event:self.zeitOf2())
        ui.bind("window", "f",lambda event:self.zeitOf3())
        ui.bind("window.text1", "<Return>", lambda event:self.zeitOf1())
        ui.bind("window.text2", "<Return>", lambda event:self.zeitOf2())
        ui.bind("window.text3", "<Return>", lambda event:self.zeitOf3())

        # add picture
        logoFile=self.__config.get("app.logo")
        if logoFile:
            self.__logo = tk.PhotoImage(name="logo", file=logoFile)
            ui.config("window.frmLogo.frmLogoImage", image=self.__logo)


        # fill list with data
        self.refeshList()

    def start(self):
        self.__clocktime()


    def __clocktime(self):
        """
        This function is used to
        display time on the label
        """
        string = time.strftime('%H:%M:%S')
        self.__ui.config("window.lblClock", text=string)
        self.__ui.after("window.lblClock", 500, self.__clocktime)

    #========================================================================
    def check_1(self):
        self.__checkNumber(1)

    def check_2(self):
        self.__checkNumber(2)

    def check_3(self):
        self.__checkNumber(3)

    def __checkNumber(self, nummer: int):
        nostr = self.__ui.getValue(f"window.text{nummer}")
        if(len(nostr)>0):
            row = self.__db.getDataByNumber(nostr)
            if row is None:
                self.__ui.config(f"window.btnCommit{nummer}", style=self.__styles["greenButton"] )
                self.__ui.config(f"window.text{nummer}", style=self.__styles["greenEntry"] )
            else:
                self.__ui.config(f"window.btnCommit{nummer}", style=self.__styles["redButton"] )
                self.__ui.config(f"window.text{nummer}", style=self.__styles["redEntry"] )

    # ============================================================================================
    def zeitOf1(self):
        self.__speichereZeit(1)

    def zeitOf2(self):
        self.__speichereZeit(2)

    def zeitOf3(self):
        self.__speichereZeit(3)


    def __speichereZeit(self, nummer: int):
        """
        speichert die Bootsnummer und die aktuelle Zeit in der Datenbank.
        """
        jetzt      = time.localtime()
        timeString = str(jetzt.tm_hour).zfill(2) + ":" + str(jetzt.tm_min).zfill(2) + ":" + str(jetzt.tm_sec).zfill(2)
        secToday   = 3600*jetzt.tm_hour + 60*jetzt.tm_min + jetzt.tm_sec
        nostr = self.__ui.getValue(f"window.text{nummer}")
        if(len(nostr)>0):
            self.__db.upsertDataByNumber(nostr, timeString, jetzt.tm_hour, jetzt.tm_min, jetzt.tm_sec, secToday)

            self.__ui.replace(f"window.text{nummer}", str(int(nostr)+1))
            self.__ui.config(f"window.btnCommit{nummer}", style=self.__styles["defaultButton"] )
            self.__ui.config(f"window.text{nummer}", style=self.__styles["defaultEntry"] )
            self.refeshList()
        else:
            self.__ui.replace(f"window.text{nummer}", "0")
            self.__ui.config(f"window.btnCommit{nummer}", style=self.__styles["redButton"] )
            self.__ui.config(f"window.text{nummer}", style=self.__styles["redEntry"] )

    #========================================================================
    def refeshList(self):
        """
        Update liste der vorhandenen nummern
        """
        #print("refeshList....")
        self.__ui.clear("window.frmEntryList.frmEntryListBox")
        data = self.__db.getAllData()
        for satz in data:
            # listbox:
            line = f"{satz[1]}    {str(satz[0]).zfill(4)}"
            if(satz[6] != 0):
                line = f"{line} (korrigiert)"
            self.__ui.insert("window.frmEntryList.frmEntryListBox", tk.END, line)

    #========================================================================
    def get4Modification(self):
        """
        Load selected entry from list into fields for editing.
        """
        entryText = self.__ui.curselection("window.frmEntryList.frmEntryListBox")
        if entryText:
            Nummer = entryText[12:16]
            self.__changeNr = int(Nummer)
            TRZtext = f"Change #{self.__changeNr}"
            self.__ui.config("window.lblChangeText", text=TRZtext)
            row = self.__db.getDataByNumber(self.__changeNr)
            if row:
                self.__ui.replace("window.editH", str(row[2]).zfill(2))
                self.__ui.replace("window.editM", str(row[3]).zfill(2))
                self.__ui.replace("window.editS", str(row[4]).zfill(2))
                myOLD = row[1]
                if(row[6] > 0):
                   oldH = math.floor(row[6] / 3600)
                   oldM = math.floor( (row[6] - 3600 * oldH) / 60)
                   oldS = row[6] - 3600 * oldH -60 * oldM
                   myOLD = myOLD + " (" + str(oldH).zfill(2) + ":" + str(oldM).zfill(2) + ":" + str(oldS).zfill(2)
                   if(row[7] > 0):
                       oldH = math.floor(row[7] / 3600)
                       oldM = math.floor( (row[7] - 3600 * oldH) / 60)
                       oldS = row[7] - 3600 * oldH -60 * oldM
                       myOLD = myOLD + " und " + str(oldH).zfill(2) + ":" + str(oldM).zfill(2) + ":" + str(oldS).zfill(2)
                   myOLD = myOLD + ")"
                else:
                   myOLD = myOLD + " <=  alte Zeit" 
                self.__ui.config("window.lblChangeStatus", text=myOLD)

    #========================================================================
    def changeTime(self):
        """
        Update changed time entry in database
        """
        if self.__changeNr != None:
            row = self.__db.getDataByNumber(self.__changeNr)
            if row:
                print(f"Change row: {row}")
                backup0 = row[5]
                backup1 = row[6]
                backup2 = row[7]
                #
                try:
                    newH    = int(self.__ui.getValue("window.editH"))
                except:
                    newH = 0
                try:
                    newM    = int(self.__ui.getValue("window.editM"))
                except:
                    newM = 0
                try:
                    newS    = int(self.__ui.getValue("window.editS"))
                except:
                    newS = 0
                timeString = str(newH).zfill(2) + ":" + str(newM).zfill(2) + ":" + str(newS).zfill(2)
                secToday = 3600 * newH + 60 * newM + newS
                #______________________________________________ gleiche Zeit?
                if(secToday == backup0):
                    print(str(self.__changeNr) + " nicht geändert ?!")
                else:
                    #
                    oldTime = row[1]
                    self.__db.updateDataByNumber(self.__changeNr, timeString, newH, newM, newS, secToday, backup0, backup1, oldTime, "Change time of")
                    print(str(self.__changeNr) + " wurde geändert")
            #---
            myOLD = "nichts mehr gewählt, zuletzt: " + str(self.__changeNr) 
            self.__ui.config("window.lblChangeStatus", text=myOLD)
            #-- clear change Nr
            self.__changeNr = None
            #---
            self.__ui.clear("window.editH")
            self.__ui.clear("window.editM")
            self.__ui.clear("window.editS")
            TRZtext = "Change with List"
            self.__ui.config("window.lblChangeText", text=TRZtext)
            # Update, da sonst verunsichernd:
            self.refeshList()


    #========================================================================
    def deleteTime(self):
        """
        Delete time entry in database
        """
        if self.__changeNr != None:
            self.__db.deleteDataByNumber(self.__changeNr)
            #---
            myOLD = "nichts mehr gewählt, zuletzt: " + str(self.__changeNr) 
            self.__ui.config("window.lblChangeStatus", text=myOLD)
            #-- clear change Nr
            self.__changeNr = None
            #---
            self.__ui.clear("window.editH")
            self.__ui.clear("window.editM")
            self.__ui.clear("window.editS")
            TRZtext = "Change with List"
            self.__ui.config("window.lblChangeText", text=TRZtext)
            # Update, da sonst verunsichernd:
            self.refeshList()

    #========================================================================
    def writeLocalTrzFile(self):
        fileName = self.__config.get("data.TRZFile")
        if self.__writeTrzFile(fileName):
            messagebox.showinfo(title="TRZ File", message=f"TRZ File '{fileName}' geschrieben.")
        else:
            messagebox.showerror(title="TRZ File", message=f"TRZ File '{fileName}' konnte nicht lokal geschrieben werden.")

    def sendFile(self):
        fileName = self.__config.get("data.TRZFile")
        dbName = self.__config.get("data.SQLiteFile")
        if self.__writeTrzFile(fileName):
            if self.__transport and self.__transport.sendFile([fileName, dbName]):
                messagebox.showinfo(title="TRZ File", message=f"TRZ File '{fileName}' erfolgreich übertragen.")
            else:
                messagebox.showerror(title="TRZ File", message=f"TRZ File '{fileName}' nicht übertragen.")
        else:
            messagebox.showerror(title="TRZ File", message=f"TRZ File '{fileName}' konnte nicht lokal geschrieben werden.")


    def __writeTrzFile(self, fileName:str) -> bool:
        # print("would now write fo file")
        try:
            with open(fileName, "w") as file:
                data = self.__db.getAllData()
                for satz in data:
                    file.write(f"{str(satz[0]).zfill(4)}\t{satz[1]}\n")
                file.close()
                return True
        except:
            return False
