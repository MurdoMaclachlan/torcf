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
from sys import argv
from time import sleep
from typing import NoReturn
from .auth import init
from .globals import Globals
from .logger import Log
from .post import add_post, check_post, find_wanted, update_post_list

global Globals, Log


def clone_finder() -> NoReturn:
    """Primary function for TCF; handles all functionality and processes.

    No arguments.

    No return value.
    """
    Notify.init("Clone Finder")
    Log.new(f"Running Clone Finder version {Globals.VERSION}", "NOSCOPE")
    Globals.process_args(argv, Log)
    reddit = init()
    if Globals.CHECK_FOR_SUB:
        Globals.get_subs()

    while True:

        # Fetch posts and set shit up
        Log.new("Fetching posts...", "INFO")
        post_list = reddit.subreddit("transcribersofreddit").new(limit=500)

        if not Globals.check_skip(post_list):
            Log.new("Posts fetched; generating list...", "INFO")
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
                    len(Globals.posts),
                    spinner='classic', bar='classic', enrich_print=False
                ) as progress:
                for post in Globals.posts:
                    check_post(post, Notify)
                    if Globals.CHECK_FOR_SUB:
                        find_wanted(post, Notify)
                    progress()

            # Write out any updated post data
            if Globals.CHECK_FOR_SUB:
                update_post_list()
            Log.new(
                f"Finished checking all posts, waiting {Globals.WAIT} seconds.",
                "INFO"
            )
        else:
            Log.new("No new posts since last check, skipping cycle.", "INFO")
            if Globals.VERBOSE:
                Notify.Notification.new("Skipping cycle.").show()
            Log.new(f"Waiting {Globals.WAIT} seconds.", "INFO")

        Log.output()
        Globals.clean()
        sleep(Globals.WAIT)