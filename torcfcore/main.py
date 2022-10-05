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

import signal
from smooth_progress import ProgressBar
from sys import argv
from sys import exit as sysexit
from time import sleep
from typing import Any
from .auth import init
from .globals import Globals, VERSION
from .logger import Log
from .post import PostHandler, check_mod_queue

global bar


def torcf() -> None:
    """Primary function for TCF; handles all functionality and processes.
    """
    global bar

    Log.new(f"Running Clone Finder version {VERSION}", "NOSCOPE")
    Globals.process_args(argv, Log)
    reddit = init()
    signal.signal(signal.SIGINT, signal_handler)
    if Globals.check_for_sub:
        Globals.get_subs()
    Globals.Handler = PostHandler()

    while True:

        # Fetch posts and set shit up
        Log.new("Fetching posts...", "INFO")
        post_list = reddit.subreddit("transcribersofreddit").new(limit=751)
        bar = ProgressBar(limit=750)

        if not Globals.Handler.check_if_skip(post_list):
            Log.new("Posts fetched; generating list...", "INFO")
            # Iterate over posts and initialise each one as a ToRPost for easier
            # management
            bar.open()
            for post in post_list:
                Globals.Handler.add_post(post)
                bar.increment()
            bar.close()
            Log.new("Checking for clones...", "INFO")
            Globals.Handler.check_posts(bar)

            # Write out any updated post data
            if Globals.check_for_sub:
                if Globals.modlog:
                    Globals.Handler.check_mod_log(
                        reddit.subreddit('transcribersofreddit').mod.log(limit=750),
                        bar
                    )
                if Globals.modqueue:
                    check_mod_queue(
                        reddit.subreddit('transcribersofreddit').mod.modqueue(limit=25),
                        reddit,
                        bar
                    )
                Globals.Handler.update_post_list()
            Log.new(
                f"Finished checking all posts, waiting {Globals.wait} seconds.",
                "INFO"
            )
        else:
            Log.new("No new posts since last check, skipping cycle.", "INFO")
            if Globals.verbose:
                Log.notify("Skipping cycle.")
            Log.new(f"Waiting {Globals.wait} seconds.", "INFO")
        Log.output()
        Globals.Handler.clean()
        sleep(Globals.wait)


def signal_handler(sig: int, frame: Any) -> None:
    """Gracefully exit; don't lose any as-yet unsaved log entries.

    :param sig: int
    :param frame: Any

    :return: Nothing.
    """
    try:
        global bar
        if not bar.close():
            print("\r", end="\r")
    except NameError:
        pass
    Log.new("Received kill signal, exiting...", "INFO")
    Log.output()
    sysexit(0)