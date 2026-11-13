"""Main application logic for RVE Zeitmessung.

Created on 18.3.2023

@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import math
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .RveZeitConfig import Config
from .RveZeitDB import DB
from .RveZeitFtp import FTP
from .RveZeitUI import UI


class App:
    """Contain the actual application code."""

    def __init__(self, config: Config, ui: UI, db: DB, transport: FTP):
        """Initialize the application, wiring up UI, database and transport."""
        self.__config: Config = config
        self.__ui: UI = ui
        self.__db: DB = db
        self.__transport: FTP = transport
        self.__changeNr = None
        self.__styles: dict[str, str] = {}

        max_number = db.get_max_number()

        # Create Styles
        green = "#109410"
        red = "#ba1c1c"
        ttk.Style().configure("green.TButton", foreground=green)
        ttk.Style().configure("red.TButton", foreground=red)
        ttk.Style().configure("green.TEntry", foreground=green)
        ttk.Style().configure("red.TEntry", foreground=red)

        self.__styles = {
            "defaultButton": "TButton",
            "greenButton": "green.TButton",
            "redButton": "red.TButton",
            "defaultEntry": "TEntry",
            "greenEntry": "green.TEntry",
            "redEntry": "red.TEntry",
        }

        # activate menues
        ui.config_menu("window.rootMenu.fileMenu", 0, command=self.send_file)
        ui.config_menu("window.rootMenu.fileMenu", 2, command=self.exit)
        ui.config_menu("window.rootMenu.helpMenu", 0, command=self.show_about)

        # activate scrollbar in listbox
        scrollbar = ui.get_widget("window.frmEntryList.frmEntryListScrollbar")
        listbox = ui.get_widget("window.frmEntryList.frmEntryListBox")
        if listbox and scrollbar:
            listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)

        # activate buttons etc
        if self.__config.get("data.AutoIncrement"):
            ui.insert("window.text1", 0, str(max_number + 1))
        ui.config("window.btnCheck1", command=self.check_1)
        ui.config("window.btnCommit1", command=self.zeit_of1)
        ui.config("window.btnUp1", command=self.number_up)
        ui.config("window.btnDown1", command=self.number_down)
        ui.config("window.btnCheck2", command=self.check_2)
        ui.config("window.btnCommit2", command=self.zeit_of2)
        ui.config("window.btnCheck3", command=self.check_3)
        ui.config("window.btnCommit3", command=self.zeit_of3)
        ui.config("window.btnUpdateList", command=self.refresh_list)
        ui.config("window.btnChangeGet", command=self.get4modification)
        ui.config("window.btnChangeSave", command=self.change_tme)
        ui.config("window.btnChangeDelete", command=self.delete_time)
        ui.config("window.btnSaveLocal", command=self.write_local_trz_file)
        ui.config("window.btnTransfer", command=self.send_file)

        # activate key actions
        ui.bind("window", "s", lambda event: self.zeit_of1())
        ui.bind("window", "d", lambda event: self.zeit_of2())
        ui.bind("window", "f", lambda event: self.zeit_of3())
        ui.bind("window", "x", lambda event: self.check_1())
        ui.bind("window", "c", lambda event: self.check_2())
        ui.bind("window", "v", lambda event: self.check_3())
        ui.bind("window.text1", "<Return>", lambda event: self.zeit_of1())
        ui.bind("window.text2", "<Return>", lambda event: self.zeit_of2())
        ui.bind("window.text3", "<Return>", lambda event: self.zeit_of3())
        ui.bind("window", "<Up>", lambda event: self.number_up())
        ui.bind("window", "<Down>", lambda event: self.number_down())
        ui.bind("window", "q", lambda event: self.exit())
        ui.bind("window", "a", lambda event: self.show_about())
        ui.bind("window", "t", lambda event: self.send_file())

        # add picture
        logo_file = self.__config.get("app.logo")
        if logo_file:
            self.__logo = tk.PhotoImage(name="logo", file=logo_file)
            ui.config("window.frmLogo.frmLogoImage", image=self.__logo)

        # fill list with data
        self.refresh_list()

        # activate radiobuttons
        self.__autoValue = tk.IntVar()
        ui.config("window.radioAutoincrement", variable=self.__autoValue, command=self.__update_auto)
        ui.config("window.radioAutoClear", variable=self.__autoValue, command=self.__update_auto)
        auto_increment = self.__config.get("data.AutoIncrement")
        if auto_increment:
            self.__autoValue.set(1)
        else:
            self.__autoValue.set(0)

    def start(self):
        """Start the application and the running clock display."""
        self.__clock_time()

    def __clock_time(self):
        """Display the current time on the label."""
        string = time.strftime("%H:%M:%S")
        self.__ui.config("window.lblClock", text=string)
        self.__ui.after("window.lblClock", 500, self.__clock_time)

    # ========================================================================
    def __update_auto(self):
        """Update the auto increment / clear functionality and the configuration."""
        new_value = self.__autoValue.get()
        self.__config.update_config("data", "AutoIncrement", new_value == 1)

    # ========================================================================
    def check_1(self):
        """Prüfe die Startnummer im ersten Eingabefeld."""
        self.__check_number(1)

    def check_2(self):
        """Prüfe die Startnummer im zweiten Eingabefeld."""
        self.__check_number(2)

    def check_3(self):
        """Prüfe die Startnummer im dritten Eingabefeld."""
        self.__check_number(3)

    def __check_number(self, number: int):
        no_str = self.__ui.get_value(f"window.text{number}")
        try:
            value = int(no_str) if no_str is not None else 0
        except (TypeError, ValueError):
            value = 0

        row = self.__db.get_data_by_number(value)
        if row is None:
            self.__ui.config(f"window.btnCommit{number}", style=self.__styles["greenButton"])
            self.__ui.config(f"window.text{number}", style=self.__styles["greenEntry"])
        else:
            self.__ui.config(f"window.btnCommit{number}", style=self.__styles["redButton"])
            self.__ui.config(f"window.text{number}", style=self.__styles["redEntry"])

    # ========================================================================
    def number_up(self):
        """Erhöhe die Startnummer im ersten Eingabefeld um eins."""
        self.__change_number(1)

    def number_down(self):
        """Verringere die Startnummer im ersten Eingabefeld um eins."""
        self.__change_number(-1)

    def __change_number(self, delta: int):
        """Ändere die Startnummer im ersten Eingabefeld um den angegebenen Wert."""
        no_str = self.__ui.get_value("window.text1")
        try:
            value = int(no_str) if no_str is not None else 0
        except (TypeError, ValueError):
            value = 0
        value = max(0, value + delta)
        self.__ui.replace("window.text1", str(value))

    # ============================================================================================
    def zeit_of1(self):
        """Speichere die Zeit für das erste Eingabefeld."""
        self.__speichere_zeit(1)

    def zeit_of2(self):
        """Speichere die Zeit für das zweite Eingabefeld."""
        self.__speichere_zeit(2)

    def zeit_of3(self):
        """Speichere die Zeit für das dritte Eingabefeld."""
        self.__speichere_zeit(3)

    def __speichere_zeit(self, number: int):
        """Speichere die Bootsnummer und die aktuelle Zeit in der Datenbank."""
        jetzt = time.localtime()
        time_string = str(jetzt.tm_hour).zfill(2) + ":" + str(jetzt.tm_min).zfill(2) + ":" + str(jetzt.tm_sec).zfill(2)
        seconds_today = 3600 * jetzt.tm_hour + 60 * jetzt.tm_min + jetzt.tm_sec
        no_str = self.__ui.get_value(f"window.text{number}")
        try:
            value = int(no_str) if no_str is not None else 0
        except (TypeError, ValueError):
            value = 0

        if value > 0:
            self.__db.upsert_data_by_number(
                value, time_string, jetzt.tm_hour, jetzt.tm_min, jetzt.tm_sec, seconds_today
            )

            if self.__config.get("data.AutoIncrement"):
                self.__ui.replace(f"window.text{number}", str(value + 1))
            else:
                self.__ui.clear(f"window.text{number}")

            self.__ui.config(f"window.btnCommit{number}", style=self.__styles["defaultButton"])
            self.__ui.config(f"window.text{number}", style=self.__styles["defaultEntry"])
            self.refresh_list()
        else:
            if self.__config.get("data.AutoIncrement"):
                self.__ui.replace(f"window.text{number}", "0")

            self.__ui.config(f"window.btnCommit{number}", style=self.__styles["redButton"])
            self.__ui.config(f"window.text{number}", style=self.__styles["redEntry"])

    # ========================================================================
    def refresh_list(self):
        """Update die Liste der vorhandenen Nummern."""
        # print("refresh_list....")
        self.__ui.clear("window.frmEntryList.frmEntryListBox")
        data = self.__db.get_all_data()
        for entry in data:
            # listbox:
            line = f"{entry[1]}    {str(entry[0]).zfill(4)}"
            if entry[6] != 0:
                line = f"{line} (korrigiert)"
            self.__ui.insert("window.frmEntryList.frmEntryListBox", tk.END, line)

    # ========================================================================
    def get4modification(self):
        """Load the selected entry from the list into the fields for editing."""
        entry_text = self.__ui.curselection("window.frmEntryList.frmEntryListBox")
        if entry_text:
            number = entry_text[12:16]
            self.__changeNr = int(number)
            trz_text = f"Change #{self.__changeNr}"
            self.__ui.config("window.lblChangeText", text=trz_text)
            row = self.__db.get_data_by_number(self.__changeNr)
            if row is not None:
                self.__ui.replace("window.editH", str(row[2]).zfill(2))
                self.__ui.replace("window.editM", str(row[3]).zfill(2))
                self.__ui.replace("window.editS", str(row[4]).zfill(2))
                old_data = row[1]
                if row[6] > 0:
                    old_hour = math.floor(row[6] / 3600)
                    old_minutes = math.floor((row[6] - 3600 * old_hour) / 60)
                    old_seconds = row[6] - 3600 * old_hour - 60 * old_minutes
                    old_data = (
                        old_data
                        + " ("
                        + str(old_hour).zfill(2)
                        + ":"
                        + str(old_minutes).zfill(2)
                        + ":"
                        + str(old_seconds).zfill(2)
                    )
                    if row[7] > 0:
                        old_hour = math.floor(row[7] / 3600)
                        old_minutes = math.floor((row[7] - 3600 * old_hour) / 60)
                        old_seconds = row[7] - 3600 * old_hour - 60 * old_minutes
                        old_data = (
                            old_data
                            + " und "
                            + str(old_hour).zfill(2)
                            + ":"
                            + str(old_minutes).zfill(2)
                            + ":"
                            + str(old_seconds).zfill(2)
                        )
                    old_data = old_data + ")"
                else:
                    old_data = old_data + " <=  alte Zeit"
                self.__ui.config("window.lblChangeStatus", text=old_data)

    # ========================================================================
    def change_tme(self):
        """Update the changed time entry in the database."""
        if self.__changeNr is not None:
            row = self.__db.get_data_by_number(self.__changeNr)
            if row is not None:
                print(f"Change row: {row}")
                backup0 = row[5]
                backup1 = row[6]
                # backup2 = row[7]
                #
                try:
                    new_hour = int(self.__ui.get_value("window.editH") or "0")
                except Exception:
                    new_hour = 0
                try:
                    new_minutes = int(self.__ui.get_value("window.editM") or "0")
                except Exception:
                    new_minutes = 0
                try:
                    new_seconds = int(self.__ui.get_value("window.editS") or "0")
                except Exception:
                    new_seconds = 0
                time_string = str(new_hour).zfill(2) + ":" + str(new_minutes).zfill(2) + ":" + str(new_seconds).zfill(2)
                seconds_today = 3600 * new_hour + 60 * new_minutes + new_seconds
                # ______________________________________________ gleiche Zeit?
                if seconds_today == backup0:
                    print(str(self.__changeNr) + " nicht geändert ?!")
                else:
                    #
                    old_time = row[1]
                    self.__db.update_data_by_number(
                        self.__changeNr,
                        time_string,
                        new_hour,
                        new_minutes,
                        new_seconds,
                        seconds_today,
                        backup0,
                        backup1,
                        old_time,
                        "Change time of",
                    )
                    print(str(self.__changeNr) + " wurde geändert")
            # ---
            old_data = "nichts mehr gewählt, zuletzt: " + str(self.__changeNr)
            self.__ui.config("window.lblChangeStatus", text=old_data)
            # -- clear change Nr
            self.__changeNr = None
            # ---
            self.__ui.clear("window.editH")
            self.__ui.clear("window.editM")
            self.__ui.clear("window.editS")
            trz_text = "Change with List"
            self.__ui.config("window.lblChangeText", text=trz_text)
            # Update, da sonst verunsichernd:
            self.refresh_list()

    # ========================================================================
    def delete_time(self):
        """Delete the time entry in the database."""
        if self.__changeNr is not None:
            self.__db.delete_data_by_number(self.__changeNr)
            # ---
            old_data = "nichts mehr gewählt, zuletzt: " + str(self.__changeNr)
            self.__ui.config("window.lblChangeStatus", text=old_data)
            # -- clear change Nr
            self.__changeNr = None
            # ---
            self.__ui.clear("window.editH")
            self.__ui.clear("window.editM")
            self.__ui.clear("window.editS")
            trz_text = "Change with List"
            self.__ui.config("window.lblChangeText", text=trz_text)
            # Update, da sonst verunsichernd:
            self.refresh_list()

    # == FTP ======================================================================
    def write_local_trz_file(self):
        """Schreibe die TRZ-Datei lokal und melde das Ergebnis dem Benutzer."""
        file_name = self.__config.get("data.TRZFile")
        if self.__write_trz_file(file_name):
            messagebox.showinfo(title="TRZ File", message=f"TRZ File '{file_name}' geschrieben.")
        else:
            messagebox.showerror(
                title="TRZ File", message=f"TRZ File '{file_name}' konnte nicht lokal geschrieben werden."
            )

    def send_file(self):
        """Schreibe die TRZ-Datei und übertrage sie zusammen mit der Datenbank per FTP."""
        file_name = self.__config.get("data.TRZFile")
        db_name = self.__config.get("data.SQLiteFile")
        if self.__write_trz_file(file_name):
            if self.__transport and self.__transport.send_file([file_name, db_name]):
                messagebox.showinfo(title="TRZ File", message=f"TRZ File '{file_name}' erfolgreich übertragen.")
            else:
                messagebox.showerror(title="TRZ File", message=f"TRZ File '{file_name}' nicht übertragen.")
        else:
            messagebox.showerror(
                title="TRZ File", message=f"TRZ File '{file_name}' konnte nicht lokal geschrieben werden."
            )

    def __write_trz_file(self, file_name: str) -> bool:
        # print("would now write fo file")
        try:
            with Path(file_name).open("w") as file:
                data = self.__db.get_all_data()
                for entry in data:
                    file.write(f"{str(entry[0]).zfill(4)}\t{entry[1]}\n")
                file.close()
                return True
        except Exception:
            return False

    # -=== Menu Handler
    def exit(self):
        """Frage den Benutzer um Bestätigung und beende die Anwendung."""
        if messagebox.askyesno("Verify", "Really quit?"):
            self.__ui.exit()

    def show_about(self):
        """Zeige den Info-Dialog mit der Anwendungsversion an."""
        messagebox.showinfo("About", f"RVEZeitmessung\n{self.__config.get('app.version')}")
