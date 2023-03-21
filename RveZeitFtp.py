#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 18.3.2023
@author: Dr. Ulf Meerwald, Martin Schmidt
"""
# ftp export
import ftplib

import RveZeitConfig


class FTP:
    """
    Class to handle ftp calls
    """

    __config = None

    def __init__(self, config: RveZeitConfig):
        self.__config = config

    def sendFile(self, files: list) -> bool:
        """
        send given files via FTP
        """
        print(f"Send {files} via FTP")
        result = False
        if self.__config:
            ftpServer = self.__config.get("ftp.FTPserver")
            ftpUser = self.__config.get("ftp.FTPuser")
            ftpPasswd = self.__config.get("ftp.FTPpasswd")
            ftpDir = self.__config.get("ftp.FTPdir")
            if ftpServer and ftpUser and ftpPasswd and ftpDir is not None:
                session = ftplib.FTP(ftpServer, ftpUser, ftpPasswd)
                if ftpDir:
                    session.cwd(ftpDir)
                # assume it works
                result = True
                for file in files:
                    try:
                        with open(file, 'rb') as fp:                        # file to send
                            session.storbinary('STOR ' + file, fp)          # send the file
                            fp.close()                                      # close file and FTP
                    except Exception:
                        result = False
                session.quit()
        if result:
            print("FTP Transfer erfolgreich !")
        return result
