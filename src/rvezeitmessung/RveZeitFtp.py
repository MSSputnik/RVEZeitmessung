#!/usr/bin/env python3
"""FTP export for RVE Zeitmessung.

Created on 18.3.2023.
@author: Dr. Ulf Meerwald, Martin Schmidt
"""

# ftp export
import ftplib
from pathlib import Path

from .RveZeitConfig import Config


class FTP:
    """Class to handle ftp calls."""

    __config = None

    def __init__(self, config: Config):
        self.__config = config

    def send_file(self, files: list[str]) -> bool:
        """Send given files via FTP."""
        print(f"Send {files} via FTP")
        result = False
        if self.__config:
            ftp_server = self.__config.get("ftp.FTPserver")
            ftp_user = self.__config.get("ftp.FTPuser")
            ftp_passwd = self.__config.get("ftp.FTPpasswd")
            ftp_dir = self.__config.get("ftp.FTPdir")
            if ftp_server and ftp_user and ftp_passwd and ftp_dir is not None:
                session = ftplib.FTP(ftp_server, ftp_user, ftp_passwd)
                if ftp_dir:
                    session.cwd(ftp_dir)
                # assume it works
                result = True
                for file in files:
                    try:
                        with Path(file).open("rb") as fp:  # file to send
                            session.storbinary("STOR " + file, fp)  # send the file
                            fp.close()  # close file and FTP
                    except Exception:
                        result = False
                session.quit()
        if result:
            print("FTP Transfer erfolgreich !")
        return result
