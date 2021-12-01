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

from typing import NoReturn


class GlobalVars:
    """Container and handler for global variables used throughout the program.

    Attributes:
        - CHECK_FOR_SUB (bool): whether or not the program should notify the user of
        posts from specific partner subs.
        - first_post_url (str): the URL of the first post in the queue on the most
        recent cycle.
        - posts (list): a list of ToRPost objects.
        - REMOVE (bool): whether or not unflaired clones should be automatically removed
        by the program.
        - skip (bool): whether or not the current cycle should be skipped.
        - VERBOSE (bool): whether or not the program should send desktop notifications
        when clones are found.
        - VERSION (str): the current version of the program.
        - WAIT (int): the number of seconds the program should wait between cycles.
        - SUBREDDITS (str): only exists if CHECK_FOR_SUBS is true; the list of partners
        to check for posts from.
        - WANTED_POSTS (list): only exists if CHECK_FOR_SUBS is true; the list of posts
        that have been found from the partners in SUBREDDITS.

    Methods:
        - clean(): empties the list of posts.
    """
    def __init__(self: object):
        self.CHECK_FOR_SUB = True
        self.first_post_url = ""
        self.posts = []
        # Remove found clones; recommended to keep disabled in the testing phase. Will
        # always need to be disabled if you aren't a moderator, as you won't have this
        # permission.
        self.REMOVE = False
        self.skip = False
        self.VERBOSE = False
        self.VERSION = "1.0.0-dev10-2021201"
        self.WAIT = 30
        if self.CHECK_FOR_SUB:
            self.SUBREDDITS = input(
                "Please enter the subreddits to search for, separated by spaces\n >> "
            ).split(" ")
            self.WANTED_POSTS = []

    def clean(self: object) -> NoReturn:
        """Deletes all currently stored members of self.POSTS.

        No arguments.

        No return value.
        """
        del self.posts[:]


class ToRPost:
    """Represents an instance of a post on the r/TranscribersOfReddit subreddit, with
    several attributes and methods which help the program investigate and manipulate the
    post.
    """
    def __eq__(self: object, other: object):
        return self.orig_link == other.orig_link

    def __init__(self: object, praw_obj: object):
        self.praw_obj = praw_obj
        self.created = self.praw_obj.created_utc
        self.flair = self.praw_obj.link_flair_text
        self.orig_link = self.praw_obj.url
        self.permalink = self.praw_obj.permalink
        self.subreddit = self.praw_obj.title.split(" |")[0]

    def update_flair(self: object, new_flair: str) -> NoReturn:
        """Updates the currently stores flair of the ToRPost with a new, given one.

        Arguments:
        - new_flair (string)

        No return value.
        """
        self.flair = new_flair

    def remove(self: object) -> NoReturn:
        """Removes the post from the ToR queue. Can only be invoked by moderators of
        r/TranscribersOfReddit; will crash the program if attempted by anyone else.

        No arguments.

        No return value.
        """
        self.praw_obj.mod.remove(mod_note="Cloned post.")


Globals = GlobalVars()