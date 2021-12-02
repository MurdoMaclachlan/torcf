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

from typing import Iterable, List, NoReturn

global Globals


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
        - VERBOSE (bool): whether or not the program should send desktop notifications
        when clones are found.
        - VERSION (str): the current version of the program.
        - WAIT (int): the number of seconds the program should wait between cycles.
        - SUBREDDITS (str): only exists if CHECK_FOR_SUBS is true; the list of partners
        to check for posts from.
        - WANTED_POSTS (list): only exists if CHECK_FOR_SUBS is true; the list of posts
        that have been found from the partners in SUBREDDITS.

    Methods:
        - check_skip(): checks whether or not the current cycle should be skipped.
        - clean(): empties the list of posts.
        - determine_wait(): determine how many seconds to wait between cycles.
        - get_subs(): get a list of subs to search for posts from.
        - process_args(): process runtime arguments.
    """
    def __init__(self: object):
        # Attributes declared here as None will be properly initialised later in the
        # run-time, depending on what arguments are passed
        self.CHECK_FOR_SUB = None
        self.REMOVE = None
        self.SUBREDDITS = None
        self.VERBOSE = None
        self.WAIT = None
        self.WANTED_POSTS = None
        # Attributes declared here should have constant initial values
        self.first_post_url = ""
        self.posts = []
        self.VERSION = "1.0.0-dev16-2021202"

    def check_skip(self: object, post_list: Iterable) -> bool:
        """Using the first_post_url value, check whether or not we should skip this
        cycle.

        Arguments:
            - post_list (Iterable): the list of posts in the queue

        Returns: a boolean success status
        """
        for post in post_list:
            post_url = f"https://reddit.com{post.permalink}"
            # If the first post in the queue is the same as it was last time we checked,
            # nothing has changed and we skip this cycle
            if self.first_post_url == post_url:
                return True
            # Else, update the URL of the first post and continue to the main checks
            else:
                self.first_post_url = post_url
                return False

    def clean(self: object) -> NoReturn:
        """Deletes all currently stored members of self.POSTS.

        No arguments.

        No return value.
        """
        del self.posts[:]

    def determine_wait(self: object, argv: List, Log: object) -> int:
        """Determine the number of seconds TCF should wait between cycles. Default to
        30 if no valid value is passed.

        Arguments:
            - argv (List): the arguments passed on running TCF

        Returns: the number of seconds the program should wait, either:
            - the argument directly succeeding "--wait"/"-w" in argv
            - default of 30 if that argument does not exist or cannot be cast to an int
        """
        index = (
            argv.index("--wait")
            if "--wait" in argv else
            argv.index("-w")
        )
        try:
            return int(argv[index+1])
        except (IndexError, ValueError):
            Log.new(
                f"{argv[index]} was passed with no subsequent value; defaulting to 30.",
                "WARNING"
            )
            return 30

    def get_subs(self: object) -> NoReturn:
        """Get, from user input, a list of subreddits to search for posts from.

        No arguments.

        No return value.
        """
        self.SUBREDDITS = input(
            "Please enter the subreddits to search for, separated by spaces.\n  >> "
        ).casefold().split(" ")
        self.WANTED_POSTS = []

    def process_args(self: object, argv: List, Log: object) -> NoReturn:
        """Process any passed runtime arguments.

        Arguments:
            - argv: the list of runtime arguments

        No return value.
        """
        self.CHECK_FOR_SUB = ("--check" in argv or "-c" in argv)
        self.REMOVE = ("--remove" in argv or "-r" in argv)
        self.VERBOSE = ("--verbose" in argv or "-v" in argv)
        self.WAIT = (
            30
            if not ("--wait" in argv or "-w" in argv) else
            self.determine_wait(argv, Log)
        )

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
        self.subreddit = self.praw_obj.title.split(" |")[0].casefold()

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