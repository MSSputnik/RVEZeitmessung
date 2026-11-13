#!/usr/bin/env python3
"""
Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import json
import tkinter as tk
from tkinter import ttk


class UI:
    """
    Class to render and show the User Interface.
    This class should not contain any handlers.
    """

    __config = None
    __baseName = "window"
    __UIElements = {}

    def __init__(self, config: dict):
        print("Init UI")
        self.__config = config
        if self.__config is not None:
            self.__createWindow()

    def __createWindow(self):
        self.__UIElements[self.__baseName] = window = tk.Tk()

        # integer validation
        self.__validationInteger = window.register(self.__only_numbers)
        self.__validationHour = window.register(self.__only_hours)
        self.__validationMinute = window.register(self.__only_minutes)

        val = self.__config.getUI("title")
        if val:
            window.title(val)
        val = self.__config.getUI("geometry")
        if val:
            window.geometry(val)
        val = self.__config.getUI("resizable")
        if val:
            window.resizable(**val)
        val = self.__config.getUI("uiElements")
        if val:
            for element in val:
                self.__addUIElement("window", element)
        val = self.__config.getUI("menu")
        if val:
            self.__addMenu("window", val)

    def __addMenu(self, base: str, element: dict):
        """
        Add Manin Menu to Window.
        Calls creation of all subsequent elements in the menu tree
        """
        # print(f"Add Menu to {base}: {element}")
        if base and base in self.__UIElements and element:
            parent = self.__UIElements[base]
            if "name" in element:
                elementName = f"{base}.{element['name']}"
                properties = {}
                if "properties" in element:
                    properties = element["properties"]
                self.__UIElements[elementName] = tk.Menu(parent, **properties)
                parent.config(menu=self.__UIElements[elementName])
                if "elements" in element:
                    for subElement in element["elements"]:
                        self.__addMenuElement(elementName, subElement)

    def __addMenuElement(self, base: str, element: dict):
        """
        Add a menu element
        """
        # print(f"* Add menu element to {base}. Element: {element}")
        if base and base in self.__UIElements and element:
            parent = self.__UIElements[base]
            if "name" in element and "type" in element:
                elementName = f"{base}.{element['name']}"
                properties = {}
                if "properties" in element:
                    properties = element["properties"]
                menuProperties = {}
                if "menuProperties" in element:
                    menuProperties = element["menuProperties"]
                type = element["type"].lower()
                if type == "cascade":
                    self.__addSubMenu(parent, elementName, properties, menuProperties)
                if type == "separator":
                    parent.add_separator()
                if type == "command":
                    parent.add_command(**properties)

                if "elements" in element:
                    for subElement in element["elements"]:
                        self.__addMenuElement(elementName, subElement)

    def __addSubMenu(self, parent, name: str, properties: dict = {}, menuProperties: dict = {}):
        """
        Add an sub menu
        """
        # print(f"** Add new Sub Menue {name}")
        self.__UIElements[name] = tk.Menu(parent, **menuProperties)
        parent.add_cascade(menu=self.__UIElements[name], **properties)

    def __addUIElement(self, base: str, element: dict):
        # print(f"Add to {base} new UI Element: {element}")
        if base and base in self.__UIElements and element:
            parent = self.__UIElements[base]
            if "name" in element and "type" in element:
                elementName = f"{base}.{element['name']}"
                properties = {}
                if "properties" in element:
                    properties = element["properties"]
                placement = {}
                if "placement" in element:
                    placement = element["placement"]
                pack = {}
                if "pack" in element:
                    pack = element["pack"]
                validation = {}
                if "validation" in element:
                    validation = element["validation"]

                if element["type"].lower() == "label":
                    self.__addLabel(parent, elementName, properties, placement, pack)
                if element["type"].lower() == "entry":
                    self.__addEntry(parent, elementName, properties, placement, pack, validation)
                if element["type"].lower() == "button":
                    self.__addButton(parent, elementName, properties, placement, pack)
                if element["type"].lower() == "frame":
                    self.__addFrame(parent, elementName, properties, placement, pack)
                if element["type"].lower() == "scrollbar":
                    self.__addScrollbar(parent, elementName, properties, placement, pack)
                if element["type"].lower() == "listbox":
                    self.__addListbox(parent, elementName, properties, placement, pack)
                if element["type"].lower() == "radiobutton":
                    self.__addRadioButton(parent, elementName, properties, placement, pack)

                if "uiElements" in element:
                    for subElement in element["uiElements"]:
                        self.__addUIElement(elementName, subElement)

    def __addLabel(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an label
        """
        # print(f"Add new label {name}")
        self.__UIElements[name] = ttk.Label(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __addEntry(
        self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}, validation: dict = {}
    ):
        """
        Add an entry
        """
        # print(f"Add new entry {name}")
        self.__UIElements[name] = ttk.Entry(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)
        if validation:
            maxLength = 0
            if "length" in validation:
                maxLength = validation["length"]
            if "type" in validation:
                validationType = validation["type"]
                if validationType.lower() == "integer":
                    self.__UIElements[name].config(
                        validate="key", validatecommand=(self.__validationInteger, "%S", "%P", maxLength)
                    )
                if validationType.lower() == "hour":
                    self.__UIElements[name].config(validate="key", validatecommand=(self.__validationHour, "%S", "%P"))
                if validationType.lower() == "minute":
                    self.__UIElements[name].config(
                        validate="key", validatecommand=(self.__validationMinute, "%S", "%P")
                    )

    def __addButton(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an button
        """
        # print(f"Add new button {name}")
        self.__UIElements[name] = ttk.Button(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __addRadioButton(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an radio button
        """
        # print(f"Add new button {name}")
        self.__UIElements[name] = ttk.Radiobutton(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __addFrame(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an frame
        """
        # print(f"Add new frame {name}")
        self.__UIElements[name] = ttk.Frame(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __addScrollbar(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an scrollbar
        """
        # print(f"Add new scrollbar {name}")
        self.__UIElements[name] = ttk.Scrollbar(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __addListbox(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an listbox
        """
        # print(f"Add new listbox {name}")
        self.__UIElements[name] = tk.Listbox(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __only_numbers(self, char, text, lenght):
        """
        Function to validate for number with max length
        """
        # print(f"Validate number: {char} - {text} - {lenght}")
        if int(lenght) > 0:
            return char.isdigit() and len(text) <= int(lenght)
        char.isdigit()

    def __only_hours(self, char, text):
        """
        Function to validate for hours 0 - 23
        """
        # print(f"Validate Hour: {char} - {text}")
        if len(text) == 0:
            return True
        try:
            return char.isdigit() and len(text) <= 2 and int(text) >= 0 and int(text) < 24
        except Exception:
            return False

    def __only_minutes(self, char, text):
        """
        Function to validate for minutes or seconds 0 - 59
        """
        # print(f"Validate Minute: {char} - {text}")
        if len(text) == 0:
            return True
        try:
            return char.isdigit() and len(text) <= 2 and int(text) >= 0 and int(text) < 60
        except Exception:
            return False

    def getWidget(self, name: str):
        """Gib das UI-Widget mit dem angegebenen Namen zurück."""
        if name and name in self.__UIElements:
            return self.__UIElements[name]

    def config(self, name: str, **values):
        """Setze Konfigurationswerte für das benannte Widget."""
        if name and name in self.__UIElements:
            self.__UIElements[name].config(values)

    def config_menu(self, name: str, index: int, **values):
        """Setze Konfigurationswerte für einen Menüeintrag am angegebenen Index."""
        if name and name in self.__UIElements:
            self.__UIElements[name].entryconfigure(index, values)

    def after(self, name: str, delay: int, callback=None):
        """Plane einen Rückruf für das benannte Widget nach der angegebenen Verzögerung."""
        if name and name in self.__UIElements:
            self.__UIElements[name].after(delay, callback)

    def show(self):
        """Zeige das Hauptfenster an und starte die Tkinter-Hauptschleife."""
        print("Show UI")
        if self.__baseName in self.__UIElements and self.__UIElements[self.__baseName] is not None:
            self.__UIElements[self.__baseName].mainloop()

    def exit(self):
        """Schließe das Hauptfenster und beende die Benutzeroberfläche."""
        print("Exit UI")
        if self.__baseName in self.__UIElements and self.__UIElements[self.__baseName] is not None:
            self.__UIElements[self.__baseName].destroy()

    def insert(self, name: str, index: int, value: str):
        """Füge einen Wert an der angegebenen Position in das benannte Widget ein."""
        # print(f"Insert into {name} at {index}: {value}")
        if name in self.__UIElements:
            self.__UIElements[name].insert(index, value)

    def clear(self, name: str):
        """Lösche den Inhalt des benannten Widgets."""
        # print(f"Clear values of {name}")
        if name in self.__UIElements:
            self.__UIElements[name].delete(0, tk.END)

    def replace(self, name: str, value: str):
        """Ersetze den Inhalt des benannten Widgets durch den angegebenen Wert."""
        # print(f"Replace value of {name}: {value}")
        if name in self.__UIElements:
            self.clear(name)
            self.insert(name, 0, value)

    def getValue(self, name: str) -> str:
        """Gib den aktuellen Wert des benannten Widgets zurück."""
        # print(f"Get value from {name}")
        if name in self.__UIElements:
            return self.__UIElements[name].get()
        return None

    def bind(self, name: str, sequence: str, func):
        """Binde eine Funktion an ein Ereignis des benannten Widgets."""
        # print(f"Bind function to {name}")
        if name in self.__UIElements:
            self.__UIElements[name].bind(sequence, func)

    def curselection(self, name: str) -> str:
        """Gib den aktuell ausgewählten Eintrag des benannten Widgets zurück."""
        # print(f"Curselection for {name}")
        lineText = None
        if name in self.__UIElements:
            lineText = self.__UIElements[name].get("anchor")
        return lineText

    def __str__(self):
        result = []
        for element in self.__UIElements:
            result.append({"name": element, "type": str(type(self.__UIElements[element]))})
        return json.dumps(result, indent=2)
