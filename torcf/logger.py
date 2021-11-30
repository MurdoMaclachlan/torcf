"""
    Copyright (C) 2021-present, Murdo B. Maclachlan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    Contact me at murdomaclachlan@duck.com
"""

from datetime import datetime
from time import time
from typing import List, NoReturn, Union


class Logger:
    def __init__(
        self: object,
        debug=0, error=1, fatal=1, info=1, warning=1
    ) -> NoReturn:
        self.__log = []
        self.__scopes = {
            "DEBUG":   debug,   # information for debugging the program
            "ERROR":   error,   # errors the program can recover from
            "FATAL":   fatal,   # errors that mean the program cannot continue
            "INFO":    info,    # general information for the user
            "WARNING": warning  # things that could cause errors later on
        }

    def get(self: object, mode="all") -> Union[List[str], str]:
        """Returns item(s) in the log, either all items or the most recently added item.

        Arguments:
        - mode (single string): options are "all" and "recent".

        Returns: a single log entry (string), list of log entries (string array), or
                 an empty string on a failure.
        """
        if mode == "all":
            return self.__log
        elif mode == "recent":
            return self.__log[len(self.__log)]
        else:
            self.new("Unknown mode passed to Logger.get().", "WARNING")
            return ""

    def get_time(self: object, method: str ="time") -> str:
        """Gets the current time and parses it to a human-readable format.

        Arguments:
        - time (int): optional with 'time.time()' as default

        Returns: a single date string in format 'YYYY-MM-DD HH:MM:SS'.
        """
        if method == "time":
            return datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")
        elif method == "date":
            return datetime.fromtimestamp(time()).strftime("%Y-%m-%d")
        else:
            print("ERROR: Bad method passed to Logger.get_time().")

    def output(self: object) -> NoReturn:
        for line in self.__log:
            with open(
                    f"data/clone_log-{self.get_time(method='date')}.txt",
                    "at+"
                ) as log_file:
                log_file.write(line + "\n")

    def new(
            self: object,
            message: str, scope: str, do_not_print: bool = False
        ) -> bool:
        """Initiates a new log entry and prints it to the console. Optionally, if
        do_not_print is passed as True, it will only save the log and will not print
        anything.

        Arguments:
        - messages (single string): the messaage to log.
        - scope (single string): the scope of the message (e.g. debug, error, info).
        - do_not_print (bool): optional, False by default.

        Returns: boolean success status.
        """
        # A select few messages should have no listed scope and should always be logged
        # and printed
        if scope == "NOSCOPE":
            self.__log.append(f"{message}")
            print(f"{message}")
            return True
        elif self.__scopes[scope]:
            self.__log.append(f"[{self.get_time()}] {scope}: {message}")
            print(
                f"[{self.get_time()}] {scope}: {message}"
                if not do_not_print
                else None
            )
            return True
        return False


global Log
Log = Logger()
