#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import gettext
import json
import tkinter as tk
import configparser


AppVersion = "20230320-1954"


class Config:
    """
    Configuration for RVE Zeit
    The program options can be retieved by the function `get(property: str)`
    The GUI layout can be retrieved by `getUI()`
    """

    __configData={}
    __uiDesign={}
    __configFileName = "RVEZeit.ini"
    __defaultPosition = "Test"
    
    __configVariables = {
        "data" : {
            "Position" : {
                "ini" : "DEFAULT.Position",
                "default" : __defaultPosition
            },
            "AutoIncrement" : {
                "ini" : "DEFAULT.AutoIncrement",
                "default" : True,
                "type" : "boolean"
            }
        },
        "ftp" : {
            "FTPserver" : {
                "ini" : "FTP.Server"
            },
            "FTPuser" : {
                "ini" : "FTP.User"
            },
            "FTPpasswd" : {
                "ini" : "FTP.Password"
            },
            "FTPdir" : {
                "ini" : "FTP.Directory"
            }
        }
    }


    def __init__(self):
        """
        Load configuration from various sources
        """

        # -- Applikationskonfiguration
        self.__configData = {}
        self.__configData["app"] = {}
        self.__configData["app"]["version"] = AppVersion
        self.__configData["app"]["title"] = f"python TriaZeit mit Datenbank - {AppVersion}"
        self.__configData["app"]["logo"] = "RVE-Logo.gif"
        self.__configData["data"] = {}
        self.__configData["data"]["Position"] = self.__defaultPosition
        # Load configuration from .ini file
        self.__loadConfigFromINI()

        # set parameter which are only nown after loading from .ini file
        self.__configData["data"]["TRZFile"] = f'{self.__configData["data"]["Position"]}.trz'
        self.__configData["data"]["SQLiteFile"] = f'{self.__configData["data"]["Position"]}.db'

        #print("Configuration")
        #print(json.dumps(self.__configData, indent=2))
        #print("--------------------------")
        #print(f'Result: {self.updateConfig("data", "AutoIncrement", False)}')
        #exit(0)
        # -- GUI Elemente
        self.__uiDesign["title"] = self.get("app.title").format(AppVersion=AppVersion)
        self.__uiDesign["geometry"] = "800x600"
        self.__uiDesign["resizable"] = {
            "width" : False,
            "height" :  False
        }
        self.__uiDesign["uiElements"] = []
        
        self.__uiDesign["uiElements"].append({
            "name" : "lblTitle",
            "type" : "label",
            "description" : "Main Title inside the application window",
            "properties" : {
                "text" : "ZEITNAHME Langstrecke ",
                "font" : ("Hack",16),
                "foreground" : "blue",
                "justify" : "left",
                "anchor" : "w"
            },
            "placement" : {
                "x" : 10,
                "y" : 5,
                "width" : 390,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "lblChangeText",
            "type" : "label",
            "description" : "Label above time change",
            "properties" : {
                "text" : "Change: -",
                "font" : ("Hack",18),
                "foreground" : "blue",
                "justify" : "left",
                "anchor" : "w"
            },
            "placement" : {
                "x" : 10,
                "y" : 110,
                "width" : 205,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "lblChangeStatus",
            "type" : "label",
            "description" : "Label below time change",
            "properties" : {
                "text" : "Noch keine Angaben",
                "font" : ("Hack",14),
                "foreground" : "blue",
                "justify" : "left",
                "anchor" : "w"
            },
            "placement" : {
                "x" : 10,
                "y" : 210,
                "width" : 400,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "lblClock",
            "type" : "label",
            "description" : "Clock",
            "properties" : {
                "text" : "00:00:00",
                "font" : ('calibri', 40, 'bold'),
                "foreground" : "white",
                "background" : "#606060",
                "justify" : tk.CENTER,
                "anchor" : tk.CENTER
            },
            "placement" : {
                "x" : 200,
                "y" : 500,
                "width" : 400,
                "height" : 80
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "frmEntryList",
            "type" : "frame",
            "description" : "Show list of already recorded number - time entries.",
            "placement" : {
                "x" : 420,
                "y" : 125,
                "width" : 350,
                "height" : 300
            },
            "uiElements" : [{
                    "name" : "frmEntryListScrollbar",
                    "type" : "scrollbar",
                    "description" : "Add scrollbar to time entries frame.",
                    "pack" : {
                        "side" : tk.RIGHT,
                         "fill" : tk.Y
                    }
                },{
                    "name" : "frmEntryListBox",
                    "type" : "listbox",
                    "description" : "Add listbox to time entries frame.",
                    "properties" : {
                        "width" : 300,
                        "font" : ("Hack",14)
                    },
                    "pack" : {
                        "side" : tk.LEFT,
                        "fill" : tk.BOTH
                    }
                }]
        })
        self.__uiDesign["uiElements"].append({
            "name" : "text1",
            "type" : "entry",
            "description" : "text entry 1",
            "validation" : {
                "type" : "integer",
                "length" : 4
            },
            "properties" : {
                "font" : ("Hack",26)
            },
            "placement" : {
                "x" : 10,
                "y" : 35,
                "width" : 85,
                "height" : 60
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnCheck1",
            "type" : "button",
            "description" : "button check for text entry 1",
            "properties" : {
                "text" : "Check"
            },
            "placement" : {
                "x" : 100,
                "y" : 35,
                "width" : 90,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnCommit1",
            "type" : "button",
            "description" : "button commit for text entry 1",
            "properties" : {
                "text" : "Zeitnahme (s)"
            },
            "placement" : {
                "x" : 100,
                "y" : 65,
                "width" : 90,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "text2",
            "type" : "entry",
            "description" : "text entry 2",
            "validation" : {
                "type" : "integer",
                "length" : 4
            },
            "properties" : {
                "font" : ("Hack",26)
            },
            "placement" : {
                "x" : 220,
                "y" : 35,
                "width" : 85,
                "height" : 60
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnCheck2",
            "type" : "button",
            "description" : "button check for text entry 2",
            "properties" : {
                "text" : "Check"
            },
            "placement" : {
                "x" : 310,
                "y" : 35,
                "width" : 90,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnCommit2",
            "type" : "button",
            "description" : "button commit for text entry 2",
            "properties" : {
                "text" : "Zeitnahme (d)"
            },
            "placement" : {
                "x" : 310,
                "y" : 65,
                "width" : 90,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "text3",
            "type" : "entry",
            "description" : "text entry 3",
            "validation" : {
                "type" : "integer",
                "length" : 4
            },
            "properties" : {
                "font" : ("Hack",26)
            },
            "placement" : {
                "x" : 430,
                "y" : 35,
                "width" : 85,
                "height" : 60
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnCheck3",
            "type" : "button",
            "description" : "button check for text entry 3",
            "properties" : {
                "text" : "Check"
            },
            "placement" : {
                "x" : 520,
                "y" : 35,
                "width" : 90,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnCommit3",
            "type" : "button",
            "description" : "button commit for text entry 3",
            "properties" : {
                "text" : "Zeitnahme (f)"
            },
            "placement" : {
                "x" : 520,
                "y" : 65,
                "width" : 90,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "editH",
            "type" : "entry",
            "description" : "text edit hour",
            "validation" : {
                "type" : "hour"
            },
            "properties" : {
                "font" : ("Hack",26)
            },
            "placement" : {
                "x" : 10,
                "y" : 145,
                "width" : 55,
                "height" : 60
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "editM",
            "type" : "entry",
            "description" : "text edit minutes",
            "validation" : {
                "type" : "minute"
            },
            "properties" : {
                "font" : ("Hack",26)
            },
            "placement" : {
                "x" : 110,
                "y" : 145,
                "width" : 55,
                "height" : 60
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "editS",
            "type" : "entry",
            "description" : "text edit seconds",
            "validation" : {
                "type" : "minute"
            },
            "properties" : {
                "font" : ("Hack",26)
            },
            "placement" : {
                "x" : 210,
                "y" : 145,
                "width" : 55,
                "height" : 60
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "lblDoppelpunkt1",
            "type" : "label",
            "description" : "Doppelpunkt zwischen editH und editM",
            "properties" : {
                "text" : ":",
                "font" : ("Hack",16),
                "foreground" : "black"
            },
            "placement" : {
                "x" : 80,
                "y" : 160
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "lblDoppelpunkt2",
            "type" : "label",
            "description" : "Doppelpunkt zwischen editM und editS",
            "properties" : {
                "text" : ":",
                "font" : ("Hack",16),
                "foreground" : "black"
            },
            "placement" : {
                "x" : 180,
                "y" : 160
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnChangeGet",
            "type" : "button",
            "description" : "button get data entry from list",
            "properties" : {
                "text" : "Get from List"
            },
            "placement" : {
                "x" : 300,
                "y" : 125,
                "width" : 100,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnChangeSave",
            "type" : "button",
            "description" : "button save changed data entry",
            "properties" : {
                "text" : "Change"
            },
            "placement" : {
                "x" : 300,
                "y" : 165,
                "width" : 100,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnChangeDelete",
            "type" : "button",
            "description" : "button delete data entry",
            "properties" : {
                "text" : "Delete"
            },
            "placement" : {
                "x" : 300,
                "y" : 205,
                "width" : 100,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnUpdateList",
            "type" : "button",
            "description" : "button update data in list",
            "properties" : {
                "text" : "Update"
            },
            "placement" : {
                "x" : 300,
                "y" : 395,
                "width" : 100,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnSaveLocal",
            "type" : "button",
            "description" : "button write local trz file",
            "properties" : {
                "text" : "Save as TRZ"
            },
            "placement" : {
                "x" : 10,
                "y" : 275,
                "width" : 100,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "btnTransfere",
            "type" : "button",
            "description" : "button start ftp transfer",
            "properties" : {
                "text" : "FTP Transfer"
            },
            "placement" : {
                "x" : 10,
                "y" : 315,
                "width" : 100,
                "height" : 30
            }
        })
        self.__uiDesign["uiElements"].append({
            "name" : "frmLogo",
            "type" : "frame",
            "description" : "Frame for logo",
            "properties" : {},
            "placement" : {
                "x" : 670,
                "y" : 10,
                "width" : 100,
                "height" : 100
            },
            "uiElements" : [
                {
                    "name" : "frmLogoImage",
                    "type" : "label",
                    "description" : "Label to hold the image",
                    "properties" : {
                        "font" : ("Hack",16),
                        "foreground" : "black"
                    },
                    "pack" : {
                        "expand" : True,
                        "fill" : tk.BOTH
                    }
                }
            ]
        })
    def __str__(self) -> str:
        """
        Get configuration as json formatted string
        """
        return json.dumps(self.__configData, indent=2)


    def get(self, property: str, default:any = None) -> any:
        """
        Get the property value.
        Separate level with `.`. e.g. Application Version: app.version
        """
        configData = None
        if property != None:
            keyList = property.split(".")
            configData = self.__configData
            for key in keyList:
                if key in configData:
                    configData = configData[key]
                else:
                    configData = None

        return configData

    def getUI(self, property: str, default:any = None) -> any:
        """
        Get the property value from the UI Design
        Separate level with `.`.
        """
        uiData = None
        if property != None:
            keyList = property.split(".")
            uiData = self.__uiDesign
            for key in keyList:
                if key in uiData:
                    uiData = uiData[key]
                else:
                    uiData = None

        return uiData
    
    def __loadConfigFromINI(self):
        """
        Load configigruation from .ini file into runtime configuration.
        Uses __configVariables to map internal to .ini variables.
        """
        config = configparser.ConfigParser()
        try:
            config.read(self.__configFileName)

            for section in self.__configVariables:
                for parameter in self.__configVariables[section]:
                    #print(f"Processing {section}.{parameter} : {self.__configVariables[section][parameter]}")
                    iniPath = None
                    value = None
                    if "ini" in self.__configVariables[section][parameter]:
                        iniPath = self.__configVariables[section][parameter]["ini"]
                    defaultValue = None
                    if "default" in self.__configVariables[section][parameter]:
                        defaultValue = self.__configVariables[section][parameter]["default"]
                    valueType = "string"
                    if "type" in self.__configVariables[section][parameter]:
                        valueType = self.__configVariables[section][parameter]["type"]
                    if iniPath:
                        iniArray = iniPath.split(".")
                        if len(iniArray) == 2:
                            #print(f"Read: {iniArray[0]} - {iniArray[1]}, Default: {defaultValue}, Type: {valueType}")
                            if valueType == "boolean":
                                value = config.getboolean(iniArray[0], iniArray[1], fallback=defaultValue)
                            if valueType == "string":
                                value = config.get(iniArray[0], iniArray[1], fallback=defaultValue)
                            if valueType == "int":
                                value = config.getint(iniArray[0], iniArray[1], fallback=defaultValue)
                            if valueType == "float":
                                value = config.getfloat(iniArray[0], iniArray[1], fallback=defaultValue)
                            if not section in self.__configData:
                                self.__configData[section] = {}
                            self.__configData[section][parameter] = value

                        else:
                            print(f"ERROR: configVariables definition error. ini path for {section}.{parameter} is invalid.")
                    else:
                        print(f"ERROR: configVariables definition error. ini path for {section}.{parameter} is missing.")
                    

        except Exception as e:
            print(f"ERROR: Laden der Konfiguration '{self.__configFileName}' fehlgeschlagen: {e}")
            exit(1)
            
    
    def updateConfig(self, section, parameter, value) -> bool:
        """
        Write the given value to the configuration .ini file.
        section and parameter are the internal values.
        They are translated by this function to the actual values for the .ini file.
        """
        result = False
        print(f"updateConfig({section}, {parameter}, {value})")
        if section and parameter:
            if section in self.__configVariables:
                if parameter in self.__configVariables[section]:
                    if "ini" in self.__configVariables[section][parameter]:
                        iniPath = self.__configVariables[section][parameter]["ini"]
                        if iniPath:
                            valueType = "string"
                            if "type" in self.__configVariables[section][parameter]:
                                valueType = self.__configVariables[section][parameter]["type"]
                            iniArray = iniPath.split(".")
                            if len(iniArray) == 2:
                                print(f"Write: {iniArray[0]} - {iniArray[1]}, Type: {valueType}, Value: {value}")
                                # After validating everything, now do the actual update.
                                config = configparser.ConfigParser()
                                config.read(self.__configFileName)
                                config.set(iniArray[0], iniArray[1], str(value))
                                with open(self.__configFileName, "w") as fp:
                                    config.write(fp, self.__configFileName)
                                    fp.close()
                            else:
                                print(f"ERROR: configVariables definition error. ini path for {section}.{parameter} is invalid.")
                        else:
                            print(f"ERROR: configVariables definition error. ini path for {section}.{parameter} is empty.")
                    else:
                        print(f"ERROR: configVariables definition error. ini path for {section}.{parameter} is missing.")
                else:
                    print(f"ERROR: updateConfig unknown parameter {parameter} in {section}.")
            else:
                print(f"ERROR: updateConfig unknown section {section}.")
        else:
            print(f"ERROR: updateConfig given section or parameter is empty.")
        return result


