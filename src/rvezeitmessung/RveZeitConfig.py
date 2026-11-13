#!/usr/bin/env python3
"""Configuration handling for RVE Zeit.

Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import configparser
import json
import tkinter as tk
from pathlib import Path
from typing import Any, ClassVar

AppVersion = "20261113-1541"


class Config:
    """Configuration for RVE Zeit.

    The program options can be retrieved by the function `get(property: str)`.
    The GUI layout can be retrieved by `get_ui()`.
    """

    __config_data: ClassVar[dict] = {}
    __ui_design: ClassVar[dict] = {}
    __config_file_name = "RVEZeit.ini"
    __default_position = "Test"

    # configVariables defines the available configuration variables
    # which can be loaded from the .ini file.
    # It maps the internal variable to the variable in the .ini file.
    # It allows the validation of the variable.
    # "internal section": {
    #   "internal parameter": {
    #     "ini": "Defines the postion in the .ini. Format: SECTION.PARAMETER",
    #     "default": "Default value",
    #     "type": "string|boolean|float|int",
    #     "min": "only for int or float. minimum allowed value. if value < minimum -> value = minimum",
    #     "max": "only for int or float. maximum allowed value. if value > maximum -> value = maximum",
    #   }
    # }
    __config_variables: ClassVar[dict] = {
        "data": {
            "Position": {"ini": "DEFAULT.Position", "default": __default_position},
            "AutoIncrement": {"ini": "DEFAULT.AutoIncrement", "default": False, "type": "boolean"},
            "InputGroups": {"ini": "DEFAULT.InputGroups", "default": 3, "type": "int", "min": 1, "max": 3},
        },
        "ftp": {
            "FTPserver": {"ini": "FTP.Server"},
            "FTPuser": {"ini": "FTP.User"},
            "FTPpasswd": {"ini": "FTP.Password"},
            "FTPdir": {"ini": "FTP.Directory"},
        },
    }

    def __init__(self):
        """Load configuration from various sources."""
        # -- Applikationskonfiguration
        self.__config_data = {}
        self.__config_data["app"] = {}
        self.__config_data["app"]["version"] = AppVersion
        self.__config_data["app"]["logo"] = "RVE-Logo.gif"
        self.__config_data["data"] = {}
        self.__config_data["data"]["Position"] = self.__default_position
        # Load configuration from .ini file
        self.__load_config_from_ini()

        # set parameter which are only nown after loading from .ini file
        self.__config_data["data"]["TRZFile"] = f"{self.__config_data['data']['Position']}.trz"
        self.__config_data["data"]["SQLiteFile"] = f"{self.__config_data['data']['Position']}.db"

        # set title wenn position ist bekannt
        self.__config_data["app"]["title"] = (
            f"python TriaZeit mit Datenbank - {AppVersion} - " + f"{self.__config_data['data']['Position']}"
        )

        # print(json.dumps(self.__config_data, indent=2))
        # print()
        # print(f"Input elements: {self.get('data.InputGroups')}")
        # exit(0)

        # -- GUI Elemente
        self.__ui_design["title"] = self.get("app.title")
        self.__ui_design["geometry"] = "800x600"
        self.__ui_design["resizable"] = {"width": False, "height": False}
        self.__ui_design["menu"] = {
            "name": "rootMenu",
            "description": "Root Menu",
            "properties": {},
            "elements": [
                {
                    "name": "fileMenu",
                    "type": "cascade",
                    "description": "File Menu",
                    "menuProperties": {"tearoff": 0},
                    "properties": {"label": "File"},
                    "elements": [
                        {
                            "name": "transfer",
                            "type": "command",
                            "description": "Transfer Command in File Menu",
                            "properties": {"label": "FTP Transfer", "accelerator": "Ctrl+T"},
                        },
                        {"name": "sep1", "type": "separator", "description": "Separator before Exit"},
                        {
                            "name": "exit",
                            "type": "command",
                            "description": "Exit Command in File Menu",
                            "properties": {"label": "Exit", "accelerator": "Ctrl+Q"},
                        },
                    ],
                },
                {
                    "name": "helpMenu",
                    "type": "cascade",
                    "description": "Help Menu",
                    "menuProperties": {"tearoff": 0},
                    "properties": {"label": "Help"},
                    "elements": [
                        {
                            "name": "about",
                            "type": "command",
                            "description": "About Command in Help Menu",
                            "properties": {"label": "About...", "accelerator": "Ctrl+A"},
                        }
                    ],
                },
            ],
        }

        # Add UI elements like labels, buttons, entries, and ...
        self.__ui_design["uiElements"] = []
        self.__ui_design["uiElements"].append(
            {
                "name": "lblTitle",
                "type": "label",
                "description": "Main Title inside the application window",
                "properties": {
                    "text": "ZEITNAHME Langstrecke ",
                    "font": ("Hack", 16),
                    "foreground": "blue",
                    "justify": "left",
                    "anchor": "w",
                },
                "placement": {"x": 10, "y": 5, "width": 390, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "lblChangeText",
                "type": "label",
                "description": "Label above time change",
                "properties": {
                    "text": "Change: -",
                    "font": ("Hack", 18),
                    "foreground": "blue",
                    "justify": "left",
                    "anchor": "w",
                },
                "placement": {"x": 10, "y": 110, "width": 205, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "lblChangeStatus",
                "type": "label",
                "description": "Label below time change",
                "properties": {
                    "text": "Noch keine Angaben",
                    "font": ("Hack", 14),
                    "foreground": "blue",
                    "justify": "left",
                    "anchor": "w",
                },
                "placement": {"x": 10, "y": 210, "width": 400, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "lblClock",
                "type": "label",
                "description": "Clock",
                "properties": {
                    "text": "00:00:00",
                    "font": ("calibri", 40, "bold"),
                    "foreground": "white",
                    "background": "#606060",
                    "justify": tk.CENTER,
                    "anchor": tk.CENTER,
                },
                "placement": {"x": 200, "y": 500, "width": 400, "height": 80},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "frmEntryList",
                "type": "frame",
                "description": "Show list of already recorded number - time entries.",
                "placement": {"x": 420, "y": 125, "width": 350, "height": 300},
                "uiElements": [
                    {
                        "name": "frmEntryListScrollbar",
                        "type": "scrollbar",
                        "description": "Add scrollbar to time entries frame.",
                        "pack": {"side": tk.RIGHT, "fill": tk.Y},
                    },
                    {
                        "name": "frmEntryListBox",
                        "type": "listbox",
                        "description": "Add listbox to time entries frame.",
                        "properties": {"width": 300, "font": ("Hack", 14)},
                        "pack": {"side": tk.LEFT, "fill": tk.BOTH},
                    },
                ],
            }
        )
        keys = ["s", "d", "f"]
        for number in range(0, self.get("data.InputGroups")):
            self.__ui_design["uiElements"].append(
                {
                    "name": f"text{number + 1}",
                    "type": "entry",
                    "description": f"text entry {number + 1}",
                    "validation": {"type": "integer", "length": 4},
                    "properties": {"font": ("Hack", 26)},
                    "placement": {"x": 10 + 210 * number, "y": 35, "width": 85, "height": 60},
                }
            )
            self.__ui_design["uiElements"].append(
                {
                    "name": f"btnCheck{number + 1}",
                    "type": "button",
                    "description": f"button check for text entry {number + 1}",
                    "properties": {"text": "Check"},
                    "placement": {"x": 100 + 210 * number, "y": 35, "width": 90, "height": 30},
                }
            )
            self.__ui_design["uiElements"].append(
                {
                    "name": f"btnCommit{number + 1}",
                    "type": "button",
                    "description": f"button commit for text entry {number + 1}",
                    "properties": {"text": f"Zeitnahme ({keys[number]})"},
                    "placement": {"x": 100 + 210 * number, "y": 65, "width": 90, "height": 30},
                }
            )
        self.__ui_design["uiElements"].append(
            {
                "name": "editH",
                "type": "entry",
                "description": "text edit hour",
                "validation": {"type": "hour"},
                "properties": {"font": ("Hack", 26)},
                "placement": {"x": 10, "y": 145, "width": 55, "height": 60},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "editM",
                "type": "entry",
                "description": "text edit minutes",
                "validation": {"type": "minute"},
                "properties": {"font": ("Hack", 26)},
                "placement": {"x": 110, "y": 145, "width": 55, "height": 60},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "editS",
                "type": "entry",
                "description": "text edit seconds",
                "validation": {"type": "minute"},
                "properties": {"font": ("Hack", 26)},
                "placement": {"x": 210, "y": 145, "width": 55, "height": 60},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "lblDoppelpunkt1",
                "type": "label",
                "description": "Doppelpunkt zwischen editH und editM",
                "properties": {"text": ":", "font": ("Hack", 16), "foreground": "black"},
                "placement": {"x": 80, "y": 160},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "lblDoppelpunkt2",
                "type": "label",
                "description": "Doppelpunkt zwischen editM und editS",
                "properties": {"text": ":", "font": ("Hack", 16), "foreground": "black"},
                "placement": {"x": 180, "y": 160},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "btnChangeGet",
                "type": "button",
                "description": "button get data entry from list",
                "properties": {"text": "Get from List"},
                "placement": {"x": 300, "y": 125, "width": 100, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "btnChangeSave",
                "type": "button",
                "description": "button save changed data entry",
                "properties": {"text": "Change"},
                "placement": {"x": 300, "y": 165, "width": 100, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "btnChangeDelete",
                "type": "button",
                "description": "button delete data entry",
                "properties": {"text": "Delete"},
                "placement": {"x": 300, "y": 205, "width": 100, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "btnUpdateList",
                "type": "button",
                "description": "button update data in list",
                "properties": {"text": "Update"},
                "placement": {"x": 300, "y": 395, "width": 100, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "btnSaveLocal",
                "type": "button",
                "description": "button write local trz file",
                "properties": {"text": "Save as TRZ"},
                "placement": {"x": 10, "y": 275, "width": 100, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "btnTransfer",
                "type": "button",
                "description": "button start ftp transfer",
                "properties": {"text": "FTP Transfer"},
                "placement": {"x": 10, "y": 315, "width": 100, "height": 30},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "radioAutoincrement",
                "type": "radiobutton",
                "description": "radio button Autoincrement",
                "properties": {"text": "Automatic Increment", "value": 1},
                "placement": {"x": 10, "y": 355, "width": 150},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "radioAutoClear",
                "type": "radiobutton",
                "description": "radio button AutoClear",
                "properties": {"text": "Automatic Clear", "value": 0},
                "placement": {"x": 10, "y": 375, "width": 150},
            }
        )
        self.__ui_design["uiElements"].append(
            {
                "name": "frmLogo",
                "type": "frame",
                "description": "Frame for logo",
                "properties": {},
                "placement": {"x": 670, "y": 10, "width": 100, "height": 100},
                "uiElements": [
                    {
                        "name": "frmLogoImage",
                        "type": "label",
                        "description": "Label to hold the image",
                        "properties": {"font": ("Hack", 16), "foreground": "black"},
                        "pack": {"expand": True, "fill": tk.BOTH},
                    }
                ],
            }
        )

    def __str__(self) -> str:
        """Return the configuration as a JSON formatted string."""
        return json.dumps(self.__config_data, indent=2)

    def get(self, prop: str, default: Any = None) -> any:
        """Get the property value.

        Separate level with `.`. e.g. Application Version: app.version
        """
        config_data = None
        if prop is not None:
            key_list = prop.split(".")
            config_data = self.__config_data
            for key in key_list:
                config_data = config_data.get(key, None)

        return config_data

    def get_ui(self, prop: str, default: Any | None = None) -> Any:
        """Get the property value from the UI design.

        Separate level with `.`.
        """
        ui_data = None
        if prop is not None:
            key_list = prop.split(".")
            ui_data = self.__ui_design
            for key in key_list:
                ui_data = ui_data.get(key, None)
        return ui_data

    def __load_config_from_ini(self):
        """Load configuration from the .ini file into runtime configuration.

        Uses __config_variables to map internal to .ini variables.
        """
        config = configparser.ConfigParser()
        try:
            config.read(self.__config_file_name)

            for section in self.__config_variables:
                for parameter in self.__config_variables[section]:
                    ini_path = None
                    value = None
                    if "ini" in self.__config_variables[section][parameter]:
                        ini_path = self.__config_variables[section][parameter]["ini"]
                    default_value = None
                    if "default" in self.__config_variables[section][parameter]:
                        default_value = self.__config_variables[section][parameter]["default"]
                    value_type = "string"
                    if "type" in self.__config_variables[section][parameter]:
                        value_type = self.__config_variables[section][parameter]["type"]
                    if ini_path:
                        ini_array = ini_path.split(".")
                        if len(ini_array) == 2:
                            if value_type == "boolean":
                                value = config.getboolean(ini_array[0], ini_array[1], fallback=default_value)
                            if value_type == "string":
                                value = config.get(ini_array[0], ini_array[1], fallback=default_value)
                            if value_type == "int":
                                value = config.getint(ini_array[0], ini_array[1], fallback=default_value)
                                if (
                                    "min" in self.__config_variables[section][parameter]
                                    and value < self.__config_variables[section][parameter]["min"]
                                ):
                                    value = self.__config_variables[section][parameter]["min"]
                                if (
                                    "max" in self.__config_variables[section][parameter]
                                    and value > self.__config_variables[section][parameter]["max"]
                                ):
                                    value = self.__config_variables[section][parameter]["max"]
                            if value_type == "float":
                                value = config.getfloat(ini_array[0], ini_array[1], fallback=default_value)
                                if (
                                    "min" in self.__config_variables[section][parameter]
                                    and value < self.__config_variables[section][parameter]["min"]
                                ):
                                    value = self.__config_variables[section][parameter]["min"]
                                if (
                                    "max" in self.__config_variables[section][parameter]
                                    and value > self.__config_variables[section][parameter]["max"]
                                ):
                                    value = self.__config_variables[section][parameter]["max"]
                            if section not in self.__config_data:
                                self.__config_data[section] = {}
                            self.__config_data[section][parameter] = value

                        else:
                            print(
                                "ERROR: configVariables definition error. "
                                + f"ini path for {section}.{parameter} is invalid."
                            )
                    else:
                        print(
                            "ERROR: configVariables definition error. "
                            + f"ini path for {section}.{parameter} is missing."
                        )
        except Exception as e:
            print(f"ERROR: Laden der Konfiguration '{self.__config_file_name}' fehlgeschlagen: {e}")
            exit(1)

    def update_config(self, section, parameter, value) -> bool:
        """Write the given value to the configuration .ini file.

        section and parameter are the internal values.
        They are translated by this function to the actual values for the .ini file.
        """
        result = False
        if section and parameter:
            if section in self.__config_variables:
                if parameter in self.__config_variables[section]:
                    if "ini" in self.__config_variables[section][parameter]:
                        ini_path = self.__config_variables[section][parameter]["ini"]
                        if ini_path:
                            value_type = "string"
                            if "type" in self.__config_variables[section][parameter]:
                                value_type = self.__config_variables[section][parameter]["type"]
                            ini_array = ini_path.split(".")
                            if len(ini_array) == 2:
                                # After validating everything, now do the actual update.
                                if section in self.__config_data:
                                    try:
                                        if value_type == "boolean":
                                            value = bool(value)
                                        if value_type == "float":
                                            value = float(value)
                                            if (
                                                "min" in self.__config_variables[section][parameter]
                                                and value < self.__config_variables[section][parameter]["min"]
                                            ):
                                                value = self.__config_variables[section][parameter]["min"]
                                            if (
                                                "max" in self.__config_variables[section][parameter]
                                                and value > self.__config_variables[section][parameter]["max"]
                                            ):
                                                value = self.__config_variables[section][parameter]["max"]
                                        if value_type == "int":
                                            value = int(value)
                                            if (
                                                "min" in self.__config_variables[section][parameter]
                                                and value < self.__config_variables[section][parameter]["min"]
                                            ):
                                                value = self.__config_variables[section][parameter]["min"]
                                            if (
                                                "max" in self.__config_variables[section][parameter]
                                                and value > self.__config_variables[section][parameter]["max"]
                                            ):
                                                value = self.__config_variables[section][parameter]["max"]
                                    except Exception:
                                        pass
                                    self.__config_data[section][parameter] = value
                                # Update .ini file
                                config = configparser.ConfigParser()
                                config.read(self.__config_file_name)
                                config.set(ini_array[0], ini_array[1], str(value))
                                with Path(self.__config_file_name).open("w") as fp:
                                    config.write(fp, self.__config_file_name)
                            else:
                                print(
                                    "ERROR: configVariables definition error. "
                                    + f"ini path for {section}.{parameter} is invalid."
                                )
                        else:
                            print(
                                "ERROR: configVariables definition error. "
                                + f"ini path for {section}.{parameter} is empty."
                            )
                    else:
                        print(
                            "ERROR: configVariables definition error. "
                            + f"ini path for {section}.{parameter} is missing."
                        )
                else:
                    print(f"ERROR: update_config unknown parameter {parameter} in {section}.")
            else:
                print(f"ERROR: update_config unknown section {section}.")
        else:
            print("ERROR: update_config given section or parameter is empty.")
        return result
