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
from os import environ, makedirs
from os.path import expanduser, isdir
from smooth_logger import Logger
from sys import platform
from typing import List, Dict


VERSION = "1.0.0-dev42-20221005"


class GlobalVars:
    """Container and handler for global variables used throughout the program.
    """
    def __init__(self):
        self.check_for_sub = False
        self.modlog = False
        self.modqueue = False
        self.remove: Dict[str, bool] = {}
        self.subreddits = False
        self.verbose = False
        self.wait = 30
        self.__get_config_path()
        self.Handler = None

    def __conf_remove(self, argv: List[str], Log: Logger) -> None:
        """
        """
        if "--remove" in argv or "-r" in argv:
            index = (
                argv.index("--remove")
                if "--remove" in argv else
                argv.index("-r")
            )
            try:
                kind = argv[index+1]
                self.remove["flaired"] = True if kind in ["all", "flaired"] else False
                self.remove["unflaired"] = (
                    True if kind in ["all", "unflaired"] else False
                )
            except IndexError:
                Log.new(
                    f"{argv[index]} was passed with no subsequent kind; defaulting to"
                    + " all.",
                    "WARNING"
                )
                self.remove["flaired"] = True
                self.remove["unflaired"] = True

    def __conf_wait(self, argv: List, Log: Logger) -> None:
        """Determine the number of seconds TCF should wait between cycles. Default to
        30 if no valid value is passed.

        :param argv: the arguments passed on running TCF

        :return: the number of seconds the program should wait, either: the argument
                 directly succeeding "--wait"/"-w" in argv, or a default of 30 if that
                 argument does not exist or cannot be cast to an int
        """
        if "--wait" in argv or "-w" in argv:
            index = (
                argv.index("--wait")
                if "--wait" in argv else
                argv.index("-w")
            )
            try:
                self.wait = abs(int(argv[index+1])); return
            except (IndexError, ValueError):
                Log.new(
                    f"{argv[index]} was passed with no subsequent time value;"
                    + " defaulting to 30.",
                    "WARNING"
                )
        self.wait = 30

    def __get_config_path(self) -> None:
        """Detects OS and defines the appropriate save path for config and logs. Exits on
        detecting an unsupported OS. Supported OSes are: Linux, MacOS, Windows.

        :return: A string dictionary containing the newly defined save paths.
        """
        home = expanduser("~")
        os = "".join(list(platform)[:3])

        # Route for a supported operating system
        if os in ["dar", "lin", "win"]:
            path = (
                environ[
                    "APPDATA"] + "\\torcf" if os == "win" else f"{home}/.config/torcf"
            )
            # Create any missing directories
            if not isdir(path):
                print(f"Making path: {path}")
                makedirs(path, exist_ok=True)
            self.config_path = path

        # Exit if the operating system is unsupported
        else:
            print(f"FATAL: Unsupported operating system: {os}, exiting.")
            exit()

    def get_subs(self) -> None:
        """Get, from user input, a list of subreddits to search for posts from.
        """
        self.subreddits = input(
            "Please enter the subreddits to search for, separated by spaces.\n  >> "
        ).casefold().split(" ")

    def process_args(self, argv: List[str], Log: Logger) -> None:
        """Process any passed runtime arguments.

        :param argv: the list of runtime arguments
        :param Log: The Logger object.
        """
        self.check_for_sub = ("--check" in argv or "-c" in argv)
        self.modlog = ("--modlog" in argv or "-l" in argv)
        self.modqueue = ("--modqueue" in argv or "-q" in argv)
        self.verbose = ("--verbose" in argv or "-v" in argv)
        self.__conf_wait(argv, Log)
        self.__conf_remove(argv, Log)

Globals = GlobalVars()