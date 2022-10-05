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
from praw.models import Submission
from smooth_logger import Logger
from typing import Iterable, List, Union, Any


VERSION = "1.0.0-dev41-20221005"


class GlobalVars:
    """Container and handler for global variables used throughout the program.
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

    def __determine_wait(self, argv: List, Log: Logger) -> None:
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
                self.WAIT = abs(int(argv[index+1])); return
            except (IndexError, ValueError):
                Log.new(
                    f"{argv[index]} was passed with no subsequent time value;"
                    + " defaulting to 30.",
                    "WARNING"
                )
        self.WAIT = 30

    def check_skip(self, post_list: Iterable) -> bool:
        """Using the first_post_url value, check whether we should skip this
        cycle.

        :param post_list: the list of posts in the queue

        :return: a boolean success status
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

    def clean(self) -> None:
        """Deletes all currently stored members of self.posts.
        """
        del self.posts[:]
        del self.removed_posts[:]

    def delete_post(self, permalink):
        """Find and delete a single member of self.posts using a given permalink.

        :param permalink: The permalink of the post to delete.
        """
        for i in self.posts:
            if i.permalink == permalink:
                self.posts.remove(i)

    def get_subs(self) -> None:
        """Get, from user input, a list of subreddits to search for posts from.
        """
        self.SUBREDDITS = input(
            "Please enter the subreddits to search for, separated by spaces.\n  >> "
        ).casefold().split(" ")
        self.removed_posts = []
        self.wanted_posts = []
        self.wanted_posts_last = [ToRPost(None, dummy=True)]

    def process_args(self, argv: List[str], Log: Logger) -> None:
        """Process any passed runtime arguments.

        :param argv: the list of runtime arguments
        :param Log: The Logger object.
        """
        self.CHECK_FOR_SUB = ("--check" in argv or "-c" in argv)
        self.MODLOG = ("--modlog" in argv or "-l" in argv)
        self.MODQUEUE = ("--modqueue" in argv or "-q" in argv)
        self.REMOVE = ("--remove" in argv or "-r" in argv)
        self.VERBOSE = ("--verbose" in argv or "-v" in argv)
        self.__determine_wait(argv, Log)

    def wanted_posts_changed(self) -> bool:
        """Check if there has been any change to the tracked posts from monitored
        subreddits.

        :return: True if there has been a change; else False.
        """
        if len(self.wanted_posts) > 0:
            for i in range(len(self.wanted_posts)):
                if self.wanted_posts[i].flair != self.wanted_posts_last[i].flair:
                    self.wanted_posts_last = self.wanted_posts
                    return True
        return False


class ToRPost:
    """Represents an instance of a post on the r/TranscribersOfReddit subreddit, with
    several attributes and methods which help the program investigate and manipulate the
    post.
    """
    def __eq__(self, other: Union[Submission, Any]):
        return self.orig_link == other.orig_link

    def __init__(self, praw_obj: Union[Submission, Any], dummy: bool = False):
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

    def update_flair(self, new_flair: str) -> None:
        """Updates the currently stored flair of the ToRPost with a new, given one.

        :param new_flair: string
        """
        self.flair = new_flair

    def remove(self, GlobalHandler: GlobalVars) -> None:
        """Removes the post from the ToR queue. Can only be invoked by moderators of
        r/TranscribersOfReddit; will crash the program if attempted by anyone else.
        """
        self.praw_obj.mod.remove(mod_note="Cloned post. (automatic removal)")
        GlobalHandler.delete_post(self.permalink)


Globals = GlobalVars()