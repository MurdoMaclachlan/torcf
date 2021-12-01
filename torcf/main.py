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

from alive_progress import alive_bar
from gi import require_version
require_version('Notify', '0.7')
from gi.repository import Notify
from time import sleep
from typing import NoReturn
from .auth import init
from .globals import Globals
from .logger import Log
from .post import add_post, check_post

global Globals, Log


def clone_finder() -> NoReturn:
    """Primary function for TCF; handles all functionality and processes.

    No arguments.

    No return value.
    """
    Notify.init("Clone Finder")
    Log.new(f"Running Clone Finder version {Globals.VERSION}", "NOSCOPE")
    reddit = init()

    while True:

        # Fetch posts and set shit up
        Log.new("Fetching posts...", "INFO")
        post_list = reddit.subreddit("transcribersofreddit").new(limit=500)
        Log.new("Posts fetched; generating list...", "INFO")

        for post in post_list:
            # If the first post in the queue is the same as it was last time we checked,
            # nothing has changed and we skip this cycle
            if Globals.first_post_url == f"https://reddit.com{post.permalink}":
                Log.new("No new posts since last check, skipping cycle.", "INFO")
                if Globals.VERBOSE:
                    Notify.Notification.new("Skipping cycle.").show()
                Globals.skip = True
                break
            # Else, update the URL of the first post and continue to the main checks
            else:
                Globals.skip = False
                Globals.first_post_url = f"https://reddit.com{post.permalink}"
                break

        if not Globals.skip:
            Log.new("Processing list...", "INFO")
            with alive_bar(
                    500, spinner='classic', bar='classic', enrich_print=False
                ) as progress:
                # Iterate over posts and initialise each one as a ToRPost for easier
                # management
                for post in post_list:
                    add_post(post)
                    progress()

            Log.new("Checking for clones...", "INFO")
            with alive_bar(
                    500, spinner='classic', bar='classic', enrich_print=False
                ) as progress:
                for post in Globals.posts:
                    # Check if clone first
                    check_post(post, Notify)

                    # Collect variables to avoid repeated calculations & improve
                    # readability
                    match_sub = (post.subreddit in Globals.SUBREDDITS)

                    if Globals.CHECK_FOR_SUB:
                        # If this post has yet to be found, add it to the list
                        if match_sub and post not in Globals.WANTED_POSTS:
                            Globals.WANTED_POSTS.append(post)
                        # If this post has been found, ensure its flair is up to date
                        # by updating the already logged post's flair with the new
                        # ToRPost instance's flair
                        elif match_sub and post in Globals.WANTED_POSTS:
                            Globals.WANTED_POSTS[
                                Globals.WANTED_POSTS.index(post)
                            ].update_flair(post.flair)
                    progress()

            # Write out any updated post data
            if Globals.CHECK_FOR_SUB:
                with open("data/post_list.txt", "w+") as post_file:
                    for i in Globals.WANTED_POSTS:
                        post_file.write(
                            f"{i.subreddit} |"
                            + f" {i.flair} |"
                            + f" https://reddit.com{i.permalink}\n"
                        )
            Log.new(
                f"Finished checking all posts, waiting {Globals.WAIT} seconds.",
                "INFO"
            )
        else:
            Log.new(f"Waiting {Globals.WAIT} seconds.", "INFO")

        Log.output()
        Globals.clean()

        sleep(Globals.WAIT)