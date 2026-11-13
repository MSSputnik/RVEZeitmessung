#!/usr/bin/env python3
"""
Aufruf des Programms.

Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

from . import RveZeitApp, RveZeitConfig, RveZeitDB, RveZeitFtp, RveZeitUI


def main():
    """Initialisiere Konfiguration, Komponenten und starte die Anwendung."""
    config = RveZeitConfig.Config()

    print(f"RVE Zeit - {config.get('app.version')}")

    transport = RveZeitFtp.FTP(config)
    db = RveZeitDB.DB(config)
    ui = RveZeitUI.UI(config)
    app = RveZeitApp.App(config, ui, db, transport)
    app.start()
    ui.show()


if __name__ == "__main__":
    main()
