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

from typing import Iterable, List

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
        - wanted_posts (list): only exists if CHECK_FOR_SUBS is true; the list of posts
        that have been found from the partners in SUBREDDITS.
        - wanted_posts_last (list): only exists if CHECK_FOR_SUBS is true; the state of
        wanted_posts at the last cycle.

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
        self.MODLOG = None
        self.MODQUEUE = None
        self.REMOVE = None
        self.SUBREDDITS = None
        self.VERBOSE = None
        self.WAIT = None
        self.removed_posts = None
        self.wanted_posts = None
        self.wanted_posts_last = None
        # Attributes declared here should have constant initial values
        self.first_post_url = ""
        self.posts = []
        self.VERSION = "1.0.0-dev38-20220817"

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

    def clean(self: object) -> None:
        """Deletes all currently stored members of self.posts.

        No arguments.

        No return value.
        """
        del self.posts[:]
        del self.removed_posts[:]

    def delete_post(self: object, permalink):
        """Find and delete a single member of self.posts using a given permalink.

        :param permalink: The permalink of the post to delete.

        No return value.
        """
        for i in self.posts:
            if i.permalink == permalink:
                self.posts.remove(i)

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
            return abs(int(argv[index+1]))
        except (IndexError, ValueError):
            Log.new(
                f"{argv[index]} was passed with no subsequent time value; defaulting to"
                + " 30.",
                "WARNING"
            )
            return 30

    def get_subs(self: object) -> None:
        """Get, from user input, a list of subreddits to search for posts from.

        :return: Nothing
        """
        self.SUBREDDITS = input(
            "Please enter the subreddits to search for, separated by spaces.\n  >> "
        ).casefold().split(" ")
        self.removed_posts = []
        self.wanted_posts = []
        self.wanted_posts_last = [ToRPost(None, dummy=True)]

    def process_args(self: object, argv: List[str], Log: object) -> None:
        """Process any passed runtime arguments.

        Arguments:
            - argv: the list of runtime arguments

        :return: Nothing
        """
        self.CHECK_FOR_SUB = ("--check" in argv or "-c" in argv)
        self.MODLOG = ("--modlog" in argv or "-l" in argv)
        self.MODQUEUE = ("--modqueue" in argv or "-q" in argv)
        self.REMOVE = ("--remove" in argv or "-r" in argv)
        self.VERBOSE = ("--verbose" in argv or "-v" in argv)
        self.WAIT = (
            30
            if not ("--wait" in argv or "-w" in argv) else
            self.determine_wait(argv, Log)
        )

    def wanted_posts_changed(self: object) -> bool:
        """Check if there has been any change to the tracked posts from monitored
        subreddits.

        :return: True if there has been a change; else False.
        """
        change = False
        if len(Globals.wanted_posts) > 0:
            for i in range(len(Globals.wanted_posts)):
                if Globals.wanted_posts[i].flair != Globals.wanted_posts_last[i].flair:
                    change = True
                    Globals.wanted_posts_last = Globals.wanted_posts
                    break
        return change


class ToRPost:
    """Represents an instance of a post on the r/TranscribersOfReddit subreddit, with
    several attributes and methods which help the program investigate and manipulate the
    post.
    """
    def __eq__(self: object, other: object):
        return self.orig_link == other.orig_link

    def __init__(self: object, praw_obj: object, dummy: bool = False):
        self.praw_obj = None
        self.created = None
        self.flair = ""
        self.orig_link = None
        self.permalink = None
        self.subreddit = None
        if not dummy:
            self.praw_obj = praw_obj
            self.created = self.praw_obj.created_utc
            self.flair = self.praw_obj.link_flair_text
            self.orig_link = self.praw_obj.url
            self.permalink = self.praw_obj.permalink
            self.subreddit = self.praw_obj.title.split(" |")[0].casefold()

    def update_flair(self: object, new_flair: str) -> None:
        """Updates the currently stored flair of the ToRPost with a new, given one.

        Arguments:
        - new_flair (string)

        No return value.
        """
        self.flair = new_flair

    def remove(self: object, GlobalHandler: object) -> None:
        """Removes the post from the ToR queue. Can only be invoked by moderators of
        r/TranscribersOfReddit; will crash the program if attempted by anyone else.

        No arguments.

        No return value.
        """
        self.praw_obj.mod.remove(mod_note="Cloned post. (automatic removal)")
        GlobalHandler.delete_post(self.permalink)


Globals = GlobalVars()