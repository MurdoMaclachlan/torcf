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
from gi import require_version
require_version('Notify', '0.7')
from gi.repository import Notify
from smooth_progress import ProgressBar
from sys import argv
from sys import exit as sysexit
from time import sleep
from typing import Any
from .auth import init
from .globals import Globals
from .logger import Log
from .post import add_post, check_mod_log, check_post, find_wanted, update_post_list

global bar, Globals, Log


def clone_finder() -> None:
    """Primary function for TCF; handles all functionality and processes.

    No arguments.

    No return value.
    """
    global bar

    Notify.init("Clone Finder")
    Log.new(f"Running Clone Finder version {Globals.VERSION}", "NOSCOPE")
    Globals.process_args(argv, Log)
    reddit = init()
    signal.signal(signal.SIGINT, signal_handler)
    if Globals.CHECK_FOR_SUB:
        Globals.get_subs()

    while True:

        # Fetch posts and set shit up
        Log.new("Fetching posts...", "INFO")
        post_list = reddit.subreddit("transcribersofreddit").new(limit=651)

        with ProgressBar(limit=650) as bar:
            if not Globals.check_skip(post_list):
                Log.new("Posts fetched; generating list...", "INFO")
                # Iterate over posts and initialise each one as a ToRPost for easier
                # management
                bar.open()
                for post in post_list:
                    add_post(post)
                    bar.increment()
                bar.close()
                Log.new("Checking for clones...", "INFO")
                bar.open()
                for post in Globals.posts:
                    check_post(post, Notify)
                    if Globals.CHECK_FOR_SUB:
                        find_wanted(post, Notify)
                    bar.increment()
                bar.close()

                # Write out any updated post data
                if Globals.CHECK_FOR_SUB:
                    if Globals.MODLOG:
                        check_mod_log(
                            reddit.subreddit('transcribersofreddit').mod.log(
                                limit=650
                            )
                        )
                    if Globals.wanted_posts != Globals.wanted_posts_last:
                        update_post_list()
                        Globals.wanted_posts_last = Globals.wanted_posts
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


def signal_handler(sig: int, frame: Any) -> None:
    """Gracefully exit; don't lose any as-yet unsaved log entries.

    :param sig: int
    :param frame: Any

    :return: Nothing.
    """
    ret = True
    try:
        global bar
        if bar.close():
            ret = False
    except NameError:
        pass
    if ret:
        print("\r", end="\r")
    Log.new("Received kill signal, exiting...", "INFO")
    Log.output()
    sysexit(0)