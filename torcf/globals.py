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


class GlobalVars:
    def __init__(self):
        self.CHECK_FOR_SUB = True
        self.DEBUG = False
        self.POSTS = []
        # Remove found clones; recommended to keep disabled in the testing phase. Will
        # always need to be disabled if you aren't a moderator, as you won't have this
        # permission.
        self.REMOVE = False
        self.skip = False
        self.VERBOSE = False
        self.VERSION = "1.0.0-dev5-20211130"
        self.WAIT = 30
        if self.CHECK_FOR_SUB:
            self.SUBREDDITS = input(
                "Please enter the subreddits to search for, separated by spaces\n >> "
            ).split(" ")


class ToRPost:
    def __init__(self: object, praw_obj: object, orig_sub: str, orig_link: str):
        self.orig_link = orig_link
        self.orig_sub = orig_sub
        self.praw_obj = praw_obj
        self.permalink = self.PRAW_OBJ.permalink

    def remove(self: object):
        self.praw_obj.mod.remove(mod_note="Cloned post.")


Globals = GlobalVars()