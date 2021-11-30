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
from time import time
from typing import Dict, NoReturn, Union
from .globals import Globals, ToRPost
from .logger import Log

global Globals, Log


def add_post(post: Submission) -> NoReturn:
    """Adds a single ToR post to the list stored in the Globals class. This contains
    information about the post itself as well as the original partner post & a method
    to remove the post from ToR.

    Arguments:
    - post (a praw.models.Submissions object)

    No return value.
    """
    Globals.POSTS.append(ToRPost(post))


def check_post(post: ToRPost, Notify: object) -> NoReturn:
    """Take a post and compare it to all subsequent posts in the queue. If any clones
    are found, delete the unflaired ones and request moderator action for the flaired
    ones.

    Arguments:
    - post (ToRPost): the post to check.
    - Notify (gi.repository.Notify): the notification manager.

    No return value.
    """
    duplicates = duplicate(post)
    if (len(i) > 0 for i in duplicates.keys()):
        Notify.Notification.new("Found cloned post.").show()
        for i in duplicates["unflaired"]:
            Log.new(
                (
                    f"Removing unflaired clone at: https://reddit.com{i.permalink}"
                    if Globals.REMOVE else
                    f"Found unflaired clone at: https://reddit.com{i.permalink}"
                ),
                "INFO"
            )
            if Globals.REMOVE: post.remove()
        for i in duplicates["flaired"]:
            Log.new(
                f"Found flaired clone at https://reddit.com{i.permalink},"
                + " moderator action required.",
                "INFO"
            )
    else:
        Log.new("Skipping post at: https://reddit.com{post.permalink}.", "DEBUG")


def duplicate(post: ToRPost) -> Dict:
    """Test if a post is a clone by checking from its position in the queue to the end
    of the queue, logging all clones encountered.

    Arguments:
    - post (ToRPost): the post to check.

    Returns: a dictionary of lists containing all found clones.
    """
    duplicates = {
        "flaired": [],
        "unflaired": []
    }
    # Skipping the queue before the post is safe to do, as we will have already checked
    # that portion for clones
    for i in Globals.POSTS[Globals.POSTS.index(post)+1:]:
        # Flaired clones are very rare but occasionally happen. The reason for them has
        # yet to be diagnosed, and we will keep them separate so they can be manually
        # inspected.
        if i == post and i.flair is not None:
            duplicates["flaired"].append(i)
        # Unflaired clones are the most common, arising from a Reddit API bug which
        # causes a failure somewhere in the flairing process, forcing Blossom to re-
        # submit the post.
        elif i == post and i.flair is None:
            duplicates["unflaired"].append(i)
        else:
            continue
    return duplicates