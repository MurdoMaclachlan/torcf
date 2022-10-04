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
from sys import platform
import smooth_logger

def get_config_path() -> str:
    """Detects OS and defines the appropriate save path for config and logs. Exits on
    detecting an unspported OS. Supported OSes are: Linux, MacOS, Windows.

    :return: A string dictionary containing the newly defined save paths.
    """
    home = expanduser("~")
    os = "".join(list(platform)[:3])

    # Route for a supported operating system
    if os in ["dar", "lin", "win"]:

        path = (
            environ["APPDATA"] + "\\torcf" if os == "win" else f"{home}/.config/torcf"
        )

        # Create any missing directories
        if not isdir(path):
            print(f"Making path: {path}")
            makedirs(path, exist_ok=True)
        return path

    # Exit if the operating system is unsupported
    else:
        print(f"FATAL: Unsupported operating system: {os}, exiting.")
        exit()

global Log
Log = smooth_logger.Logger("TORCF", get_config_path())
Log.add_scope("CLONE", 2)