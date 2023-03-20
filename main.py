#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

import RveZeitConfig
import RveZeitDB
import RveZeitApp
import RveZeitUI
import RveZeitFtp

def main():
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
