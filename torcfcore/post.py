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
from praw import Reddit
from praw.models import Submission
from smooth_progress import ProgressBar
from typing import Any, Iterable, List, Union
from .globals import Globals
from .logger import Log


class ToRPost:
    """Represents an instance of a post on the r/TranscribersOfReddit subreddit, with
    several attributes and methods which help the program investigate and manipulate the
    post.
    """
    def __eq__(self, other: Union[Submission, Any]):
        return self.orig_link == other.orig_link

    def __init__(self, praw_obj: Union[Submission, Any], dummy: bool = False):
        self.flair_last = ""
        if dummy:
            self.praw_obj = None
            self.created = None
            self.flair = ""
            self.orig_link = None
            self.permalink = None
            self.subreddit = None
        else:
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
        self.flair_last = self.flair
        self.flair = new_flair

    def remove(self, Handler) -> None:
        """Removes the post from the ToR queue. Can only be invoked by moderators of
        r/TranscribersOfReddit; will crash the program if attempted by anyone else.
        """
        self.praw_obj.mod.remove(mod_note="Cloned post. (automatic removal)")
        Handler.delete_post(self.permalink)


class ClonedPost:
    """
    """
    def __eq__(self, other) -> bool:
        return self.__original == other.__original

    def __init__(self, original: ToRPost) -> None:
        self.__flaired: List[ToRPost] = []
        self.__original: ToRPost = original
        self.__unflaired: List[ToRPost] = []

    def add_clone(self, clone: ToRPost, kind: int) -> None:
        """
        """
        if kind == 0:
            self.__flaired.append(clone)
        elif kind == 1:
            self.__unflaired.append(clone)
        else:
            Log.new(
                "Clone of unknown kind passed to ClonedPost instance; will be ignored.",
                "WARNING"
            )

    def get_original(self) -> ToRPost:
        """
        """
        return self.__original

    def remove_clones(self, Handler) -> None:
        """
        """
        for clone in self.__flaired:
            if Globals.REMOVE["flaired"]:
                clone.remove(Handler)
                Log.new(f"Removed flaired clone: {clone.permalink}", "CLONE")
            else:
                Log.new(
                    f"Not removing flaired clone at: ({clone.permalink}).", "CLONE"
                )
        for clone in self.__unflaired:
            if Globals.REMOVE["unflaired"]:
                clone.remove(Handler)
                Log.new(f"Removed unflaired clone: {clone.permalink}", "CLONE")
            else:
                Log.new(
                    f"Not removing unflaired clone at: ({clone.permalink}).",
                    "CLONE"
                )


class PostHandler:
    """Contains and handles all post entities.
    """
    def __init__(self) -> None:
        self.__first_post_url = ""
        self.__posts: List[ToRPost] = []
        self.__clones: List[ClonedPost] = []
        self.__wanted_posts: List[ToRPost] = []

    def add_post(self, post: Submission) -> None:
        """:param post: a praw.models.Submissions object
        """
        tor_post = ToRPost(post)
        self.__posts.append(tor_post)
        # Check if this post is from one of the subreddits we are looking for, and
        # handle accordingly
        if Globals.check_for_sub and tor_post.subreddit in Globals.subreddits:
            # If we're already tracking the post, we just need to update its flair
            if tor_post in self.__wanted_posts:
                self.__wanted_posts[
                    self.__wanted_posts.index(tor_post)
                ].update_flair(tor_post.flair)
            else:
                Log.notify(f"Found {tor_post.subreddit} post.")
                self.__wanted_posts.append(tor_post)

    def check_mod_log(self, modlog: Iterable, bar: ProgressBar) -> None:
        """Checks the mod log of r/TranscribersOfReddit for any post removals.

        :param modlog: a praw modlog object
        :param bar:    a smooth_progress.ProgressBar object

        :return: Nothing
        """
        Log.new("Checking modlog...", "INFO")
        removed_posts: List = []
        bar.open()
        for log in modlog:
            if log.action == "removelink":
                removed_posts.append(log.target_permalink)
            bar.increment()
        bar.close()
        for post in self.__wanted_posts:
            if post.flair != "Completed!" and post.permalink in removed_posts:
                self.__wanted_posts[
                    self.__wanted_posts.index(post)
                ].update_flair("Removed")

    def check_posts(self, bar: ProgressBar) -> None:
        """
        """
        bar.open()
        for post in self.__posts:
            self.check_single_post(post)
            bar.increment()
        bar.close()

    def check_single_post(self, post: ToRPost) -> None:
        """Test if a post is a clone by checking from its position in the queue to the
        end of the queue, logging all clones encountered.

        :param post: ToRPost; the post to check.

        :return: a dictionary of lists containing all found clones.
        """
        # First we check if we already have a clone entry for this post
        for clone_entry in self.__clones:
            if clone_entry.get_original() == post:
                Log.notify("Found cloned post.")
                clone_entry.add_clone(post, (1 if post.flair is None else 0))
        # If not, we check posts ahead of this one in the queue; skipping the queue
        # before the post is safe to do, as we will have already checked that portion
        for potential_clone in self.__posts[self.__posts.index(post) + 1:]:
            if potential_clone == post:
                Log.notify("Found cloned post.")
                clone: ClonedPost = ClonedPost(post)
                # Unflaired clones are now extremely rare and theoretically should not
                # happen, but we will keep checking for them just in case.
                if potential_clone.flair is None:
                    clone.add_clone(potential_clone, 1)
                # Flaired clones are now the only type of clone that should appear.
                else:
                    clone.add_clone(potential_clone, 0)
            else:
                Log.new(
                    f"Skipping post at: https://reddit.com{post.permalink}.", "DEBUG"
                )

    def check_if_skip(self, post_list: Iterable) -> bool:
        """Using the first_post_url value, check whether we should skip this
        cycle.

        :param post_list: the list of posts in the queue

        :return: a boolean success status
        """
        for post in post_list:
            post_url = f"https://reddit.com{post.permalink}"
            # If the first post in the queue is the same as it was last time we checked,
            # nothing has changed and we skip this cycle
            if self.__first_post_url == post_url:
                return True
            # Else, update the URL of the first post and continue to the main checks
            else:
                self.__first_post_url = post_url
                return False

    def clean(self) -> None:
        """Deletes all currently stored members of self.posts.
        """
        del self.__posts[:]

    def delete_post(self, permalink) -> None:
        """Find and delete a single member of self.posts using a given permalink.

        :param permalink: The permalink of the post to delete.
        """
        for i in self.__posts:
            if i.permalink == permalink:
                self.__posts.remove(i)
                break

    def remove_clones(self) -> None:
        """
        """
        for clone in self.__clones:
            clone.remove_clones(self)

    def update_post_list(self) -> None:
        """Write out current data within Globals.WANTED_POSTS to the post_list file,
        overwriting the data that was previously in that file.

        :return: Nothing
        """
        changed = False
        for post in self.__wanted_posts:
            if post.flair != post.flair_last:
                changed = True
        if changed:
            with open(f"{Globals.config_path}/post_list.txt", "w+") as post_file:
                for post in self.__wanted_posts:
                    post_file.write(
                        f"{post.subreddit} | "
                        + f"{post.flair} | "
                        + f"https://reddit.com{post.permalink}\n"
                    )


def check_mod_queue(modqueue: Iterable, reddit: Reddit, bar: ProgressBar) -> None:
    """Checks the mod queue of r/TranscribersOfReddit for any posts reported as removed,
    checks if they are removed, and removes them if so.

    :param modqueue: a praw modqueue object
    :param reddit:   a praw Reddit object
    :param bar:      a smooth_progress.ProgressBar object

    :return: Nothing
    """
    Log.new("Checking modqueue...", "INFO")
    bar.open()
    for item in modqueue:
        try:
            if reddit.submission(url=item.url).removed_by_category:
                Log.new("Found removed item in modqueue; removing.", "INFO")
                item.mod.remove()
        except AttributeError:
            pass
        bar.increment()
    bar.close()