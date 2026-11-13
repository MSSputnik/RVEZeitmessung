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
            self.__create_window()

    def __create_window(self):
        self.__UIElements[self.__baseName] = window = tk.Tk()

        # integer validation
        self.__validationInteger = window.register(self.__only_numbers)
        self.__validationHour = window.register(self.__only_hours)
        self.__validationMinute = window.register(self.__only_minutes)

        val = self.__config.get_ui("title")
        if val:
            window.title(val)
        val = self.__config.get_ui("geometry")
        if val:
            window.geometry(val)
        val = self.__config.get_ui("resizable")
        if val:
            window.resizable(**val)
        val = self.__config.get_ui("uiElements")
        if val:
            for element in val:
                self.__add_ui_element("window", element)
        val = self.__config.get_ui("menu")
        if val:
            self.__add_menu("window", val)

    def __add_menu(self, base: str, element: dict):
        """
        Add Manin Menu to Window.
        Calls creation of all subsequent elements in the menu tree
        """
        # print(f"Add Menu to {base}: {element}")
        if base and base in self.__UIElements and element:
            parent = self.__UIElements[base]
            if "name" in element:
                element_name = f"{base}.{element['name']}"
                properties = {}
                if "properties" in element:
                    properties = element["properties"]
                self.__UIElements[element_name] = tk.Menu(parent, **properties)
                parent.config(menu=self.__UIElements[element_name])
                if "elements" in element:
                    for sub_element in element["elements"]:
                        self.__add_menu_element(element_name, sub_element)

    def __add_menu_element(self, base: str, element: dict):
        """
        Add a menu element
        """
        # print(f"* Add menu element to {base}. Element: {element}")
        if base and base in self.__UIElements and element:
            parent = self.__UIElements[base]
            if "name" in element and "type" in element:
                element_name = f"{base}.{element['name']}"
                properties = {}
                if "properties" in element:
                    properties = element["properties"]
                menu_properties = {}
                if "menuProperties" in element:
                    menu_properties = element["menuProperties"]
                type = element["type"].lower()
                if type == "cascade":
                    self.__add_sub_menu(parent, element_name, properties, menu_properties)
                if type == "separator":
                    parent.add_separator()
                if type == "command":
                    parent.add_command(**properties)

                if "elements" in element:
                    for sub_element in element["elements"]:
                        self.__add_menu_element(element_name, sub_element)

    def __add_sub_menu(self, parent, name: str, properties: dict = {}, menuProperties: dict = {}):
        """
        Add an sub menu
        """
        # print(f"** Add new Sub Menue {name}")
        self.__UIElements[name] = tk.Menu(parent, **menuProperties)
        parent.add_cascade(menu=self.__UIElements[name], **properties)

    def __add_ui_element(self, base: str, element: dict):
        # print(f"Add to {base} new UI Element: {element}")
        if base and base in self.__UIElements and element:
            parent = self.__UIElements[base]
            if "name" in element and "type" in element:
                element_name = f"{base}.{element['name']}"
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
                    self.__add_label(parent, element_name, properties, placement, pack)
                if element["type"].lower() == "entry":
                    self.__add_entry(parent, element_name, properties, placement, pack, validation)
                if element["type"].lower() == "button":
                    self.__add_button(parent, element_name, properties, placement, pack)
                if element["type"].lower() == "frame":
                    self.__add_frame(parent, element_name, properties, placement, pack)
                if element["type"].lower() == "scrollbar":
                    self.__add_scrollbar(parent, element_name, properties, placement, pack)
                if element["type"].lower() == "listbox":
                    self.__add_listbox(parent, element_name, properties, placement, pack)
                if element["type"].lower() == "radiobutton":
                    self.__add_radio_button(parent, element_name, properties, placement, pack)

                if "uiElements" in element:
                    for sub_element in element["uiElements"]:
                        self.__add_ui_element(element_name, sub_element)

    def __add_label(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an label
        """
        # print(f"Add new label {name}")
        self.__UIElements[name] = ttk.Label(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __add_entry(
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
            max_length = 0
            if "length" in validation:
                max_length = validation["length"]
            if "type" in validation:
                validation_type = validation["type"]
                if validation_type.lower() == "integer":
                    self.__UIElements[name].config(
                        validate="key", validatecommand=(self.__validationInteger, "%S", "%P", max_length)
                    )
                if validation_type.lower() == "hour":
                    self.__UIElements[name].config(validate="key", validatecommand=(self.__validationHour, "%S", "%P"))
                if validation_type.lower() == "minute":
                    self.__UIElements[name].config(
                        validate="key", validatecommand=(self.__validationMinute, "%S", "%P")
                    )

    def __add_button(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an button
        """
        # print(f"Add new button {name}")
        self.__UIElements[name] = ttk.Button(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __add_radio_button(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an radio button
        """
        # print(f"Add new button {name}")
        self.__UIElements[name] = ttk.Radiobutton(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __add_frame(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an frame
        """
        # print(f"Add new frame {name}")
        self.__UIElements[name] = ttk.Frame(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __add_scrollbar(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
        """
        Add an scrollbar
        """
        # print(f"Add new scrollbar {name}")
        self.__UIElements[name] = ttk.Scrollbar(parent, **properties)
        if placement:
            self.__UIElements[name].place(cnf=placement)
        if pack:
            self.__UIElements[name].pack(cnf=pack)

    def __add_listbox(self, parent, name: str, properties: dict = {}, placement: dict = {}, pack: dict = {}):
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

    def get_widget(self, name: str):
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

    def get_value(self, name: str) -> str:
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
        line_text = None
        if name in self.__UIElements:
            line_text = self.__UIElements[name].get("anchor")
        return line_text

    def __str__(self):
        result = []
        for element in self.__UIElements:
            result.append({"name": element, "type": str(type(self.__UIElements[element]))})
        return json.dumps(result, indent=2)
