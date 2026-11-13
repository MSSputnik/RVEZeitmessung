"""Render and show the User Interface.

Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import json
import tkinter as tk
from tkinter import ttk
from typing import Any, override

from .RveZeitConfig import Config


class UI:
    """
    Class to render and show the User Interface.

    This class should not contain any handlers.
    """

    __base_name = "window"

    def __init__(self, config: Config):
        print("Init UI")
        self.__ui_elements: dict[str, Any] = {}
        self.__config = config
        self.__create_window()

    def __create_window(self):
        self.__ui_elements[self.__base_name] = window = tk.Tk()

        # integer validation
        self.__validation_integer = window.register(self.__only_numbers)
        self.__validation_hour = window.register(self.__only_hours)
        self.__validation_minute = window.register(self.__only_minutes)

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

    def __add_menu(self, base: str, element: dict[str, Any]):
        """Add the main menu to the window.

        Calls creation of all subsequent elements in the menu tree.
        """
        # print(f"Add Menu to {base}: {element}")
        if base and base in self.__ui_elements and element:
            parent = self.__ui_elements[base]
            if "name" in element:
                element_name = f"{base}.{element['name']}"
                properties = {}
                if "properties" in element:
                    properties = element["properties"]
                self.__ui_elements[element_name] = tk.Menu(parent, **properties)
                parent.config(menu=self.__ui_elements[element_name])
                if "elements" in element:
                    for sub_element in element["elements"]:
                        self.__add_menu_element(element_name, sub_element)

    def __add_menu_element(self, base: str, element: dict[str, Any]):
        """Add a menu element."""
        # print(f"* Add menu element to {base}. Element: {element}")
        if base and base in self.__ui_elements and element:
            parent = self.__ui_elements[base]
            if "name" in element and "type" in element:
                element_name = f"{base}.{element['name']}"
                properties = {}
                if "properties" in element:
                    properties = element["properties"]
                menu_properties = {}
                if "menuProperties" in element:
                    menu_properties = element["menuProperties"]
                type_element = element["type"].lower()
                if type_element == "cascade":
                    self.__add_sub_menu(parent, element_name, properties, menu_properties)
                if type_element == "separator":
                    parent.add_separator()
                if type_element == "command":
                    parent.add_command(**properties)

                if "elements" in element:
                    for sub_element in element["elements"]:
                        self.__add_menu_element(element_name, sub_element)

    def __add_sub_menu(
        self, parent, name: str, properties: dict[str, Any] | None = None, menu_properties: dict[str, Any] | None = None
    ):
        """Add a sub menu."""
        # print(f"** Add new Sub Menue {name}")
        if properties is None:
            properties = {}
        if menu_properties is None:
            menu_properties = {}
        self.__ui_elements[name] = tk.Menu(parent, **menu_properties)
        parent.add_cascade(menu=self.__ui_elements[name], **properties)

    def __add_ui_element(self, base: str, element: dict[str, Any]):
        # print(f"Add to {base} new UI Element: {element}")
        if base and base in self.__ui_elements and element:
            parent = self.__ui_elements[base]
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

    def __add_label(
        self,
        parent,
        name: str,
        properties: dict[str, Any] | None = None,
        placement: dict[str, Any] | None = None,
        pack: dict[str, Any] | None = None,
    ):
        """Add a label."""
        # print(f"Add new label {name}")
        if properties is None:
            properties = {}
        if placement is None:
            placement = {}
        if pack is None:
            pack = {}
        self.__ui_elements[name] = ttk.Label(parent, **properties)
        if placement:
            self.__ui_elements[name].place(cnf=placement)
        if pack:
            self.__ui_elements[name].pack(cnf=pack)

    def __add_entry(
        self,
        parent,
        name: str,
        properties: dict[str, Any] | None = None,
        placement: dict[str, Any] | None = None,
        pack: dict[str, Any] | None = None,
        validation: dict[str, Any] | None = None,
    ):
        """Add an entry."""
        # print(f"Add new entry {name}")
        if properties is None:
            properties = {}
        if placement is None:
            placement = {}
        if pack is None:
            pack = {}
        if validation is None:
            validation = {}
        self.__ui_elements[name] = ttk.Entry(parent, **properties)
        if placement:
            self.__ui_elements[name].place(cnf=placement)
        if pack:
            self.__ui_elements[name].pack(cnf=pack)
        if validation:
            max_length = 0
            if "length" in validation:
                max_length = validation["length"]
            if "type" in validation:
                validation_type = validation["type"]
                if validation_type.lower() == "integer":
                    self.__ui_elements[name].config(
                        validate="key", validatecommand=(self.__validation_integer, "%S", "%P", max_length)
                    )
                if validation_type.lower() == "hour":
                    self.__ui_elements[name].config(
                        validate="key", validatecommand=(self.__validation_hour, "%S", "%P")
                    )
                if validation_type.lower() == "minute":
                    self.__ui_elements[name].config(
                        validate="key", validatecommand=(self.__validation_minute, "%S", "%P")
                    )

    def __add_button(
        self,
        parent,
        name: str,
        properties: dict[str, Any] | None = None,
        placement: dict[str, Any] | None = None,
        pack: dict[str, Any] | None = None,
    ):
        """Add a button."""
        # print(f"Add new button {name}")
        if properties is None:
            properties = {}
        if placement is None:
            placement = {}
        if pack is None:
            pack = {}
        self.__ui_elements[name] = ttk.Button(parent, **properties)
        if placement:
            self.__ui_elements[name].place(cnf=placement)
        if pack:
            self.__ui_elements[name].pack(cnf=pack)

    def __add_radio_button(
        self,
        parent,
        name: str,
        properties: dict[str, Any] | None = None,
        placement: dict[str, Any] | None = None,
        pack: dict[str, Any] | None = None,
    ):
        """Add a radio button."""
        # print(f"Add new button {name}")
        if properties is None:
            properties = {}
        if placement is None:
            placement = {}
        if pack is None:
            pack = {}
        self.__ui_elements[name] = ttk.Radiobutton(parent, **properties)
        if placement:
            self.__ui_elements[name].place(cnf=placement)
        if pack:
            self.__ui_elements[name].pack(cnf=pack)

    def __add_frame(
        self,
        parent,
        name: str,
        properties: dict[str, Any] | None = None,
        placement: dict[str, Any] | None = None,
        pack: dict[str, Any] | None = None,
    ):
        """Add a frame."""
        # print(f"Add new frame {name}")
        if properties is None:
            properties = {}
        if placement is None:
            placement = {}
        if pack is None:
            pack = {}
        self.__ui_elements[name] = ttk.Frame(parent, **properties)
        if placement:
            self.__ui_elements[name].place(cnf=placement)
        if pack:
            self.__ui_elements[name].pack(cnf=pack)

    def __add_scrollbar(
        self,
        parent,
        name: str,
        properties: dict[str, Any] | None = None,
        placement: dict[str, Any] | None = None,
        pack: dict[str, Any] | None = None,
    ):
        """Add a scrollbar."""
        # print(f"Add new scrollbar {name}")
        if properties is None:
            properties = {}
        if placement is None:
            placement = {}
        if pack is None:
            pack = {}
        self.__ui_elements[name] = ttk.Scrollbar(parent, **properties)
        if placement:
            self.__ui_elements[name].place(cnf=placement)
        if pack:
            self.__ui_elements[name].pack(cnf=pack)

    def __add_listbox(
        self,
        parent,
        name: str,
        properties: dict[str, Any] | None = None,
        placement: dict[str, Any] | None = None,
        pack: dict[str, Any] | None = None,
    ):
        """Add a listbox."""
        # print(f"Add new listbox {name}")
        if properties is None:
            properties = {}
        if placement is None:
            placement = {}
        if pack is None:
            pack = {}
        self.__ui_elements[name] = tk.Listbox(parent, **properties)
        if placement:
            self.__ui_elements[name].place(cnf=placement)
        if pack:
            self.__ui_elements[name].pack(cnf=pack)

    def __only_numbers(self, char, text, length):
        """Validate input as a number with a maximum length."""
        # print(f"Validate number: {char} - {text} - {length}")
        if int(length) > 0:
            return char.isdigit() and len(text) <= int(length)
        char.isdigit()

    def __only_hours(self, char, text):
        """Validate input as an hour value from 0 to 23."""
        # print(f"Validate Hour: {char} - {text}")
        if len(text) == 0:
            return True
        try:
            return char.isdigit() and len(text) <= 2 and int(text) >= 0 and int(text) < 24
        except Exception:
            return False

    def __only_minutes(self, char, text):
        """Validate input as a minute or second value from 0 to 59."""
        # print(f"Validate Minute: {char} - {text}")
        if len(text) == 0:
            return True
        try:
            return char.isdigit() and len(text) <= 2 and int(text) >= 0 and int(text) < 60
        except Exception:
            return False

    def get_widget(self, name: str):
        """Gib das UI-Widget mit dem angegebenen Namen zurück."""
        if name and name in self.__ui_elements:
            return self.__ui_elements[name]

    def config(self, name: str, **values):
        """Setze Konfigurationswerte für das benannte Widget."""
        if name and name in self.__ui_elements:
            self.__ui_elements[name].config(values)

    def config_menu(self, name: str, index: int, **values):
        """Setze Konfigurationswerte für einen Menüeintrag am angegebenen Index."""
        if name and name in self.__ui_elements:
            self.__ui_elements[name].entryconfigure(index, values)

    def after(self, name: str, delay: int, callback=None):
        """Plane einen Rückruf für das benannte Widget nach der angegebenen Verzögerung."""
        if name and name in self.__ui_elements:
            self.__ui_elements[name].after(delay, callback)

    def show(self):
        """Zeige das Hauptfenster an und starte die Tkinter-Hauptschleife."""
        print("Show UI")
        if self.__base_name in self.__ui_elements and self.__ui_elements[self.__base_name] is not None:
            self.__ui_elements[self.__base_name].mainloop()

    def exit(self):
        """Schließe das Hauptfenster und beende die Benutzeroberfläche."""
        print("Exit UI")
        if self.__base_name in self.__ui_elements and self.__ui_elements[self.__base_name] is not None:
            self.__ui_elements[self.__base_name].destroy()

    def insert(self, name: str, index: int | str, value: str):
        """Füge einen Wert an der angegebenen Position in das benannte Widget ein."""
        # print(f"Insert into {name} at {index}: {value}")
        if name in self.__ui_elements:
            self.__ui_elements[name].insert(index, value)

    def clear(self, name: str):
        """Lösche den Inhalt des benannten Widgets."""
        # print(f"Clear values of {name}")
        if name in self.__ui_elements:
            self.__ui_elements[name].delete(0, tk.END)

    def replace(self, name: str, value: str):
        """Ersetze den Inhalt des benannten Widgets durch den angegebenen Wert."""
        # print(f"Replace value of {name}: {value}")
        if name in self.__ui_elements:
            self.clear(name)
            self.insert(name, 0, value)

    def get_value(self, name: str) -> str | None:
        """Gib den aktuellen Wert des benannten Widgets zurück."""
        # print(f"Get value from {name}")
        if name in self.__ui_elements:
            return str(self.__ui_elements[name].get())
        return None

    def bind(self, name: str, sequence: str, func):
        """Binde eine Funktion an ein Ereignis des benannten Widgets."""
        # print(f"Bind function to {name}")
        if name in self.__ui_elements:
            self.__ui_elements[name].bind(sequence, func)

    def curselection(self, name: str) -> Any:
        """Gib den aktuell ausgewählten Eintrag des benannten Widgets zurück."""
        # print(f"Curselection for {name}")
        line_text = None
        if name in self.__ui_elements:
            line_text = self.__ui_elements[name].get("anchor")
        return line_text

    @override
    def __str__(self):
        """Return a JSON representation of all registered UI elements."""
        result = []
        for element in self.__ui_elements:
            result.append({"name": element, "type": str(type(self.__ui_elements[element]))})
        return json.dumps(result, indent=2)
