## Unreleased

As of this version, PRAW 7.5+ and smooth_progress 0.1+ are required. PyGObject 3.42+ is now explicitly required, having been an implicit requirement before.

- Restructured program, delegating many functions from main to other modules. (@MurdoMaclachlan)
- Added and enforced refresh tokens for Reddit authentication. (@MurdoMaclachlan)
- Added the ability to search for posts from a certain sub within the queue, keeping track of their flair and link in a .txt file and sending a desktop notification when a new post from that sub is found in the queue. (@MurdoMaclachlan)
- Added various runtime arguments:
    - --check, -c: determines whether to search for posts from a certain sub; prompts what subs to search for.
    - --modlog, -m: determines whether to check modlog; requires moderator privileges. Will allow tracking of removed posts.
    - --remove, -r: determines whether clones should be automatically removed; requires moderator privileges.
    - --verbose, -v: provides extra logging and desktop notifications.
    - --wait, -w: how long in seconds the program should wait in between checks; defaults to 30; format: `--wait X`
- Added ability to auto-remove clones; disabled by default, requires moderator privileges. (@MurdoMaclachlan)
- Increased post limit for Reddit instance from 500 to 651 to account for increasing queue sizes. (@MurdoMaclachlan)
- Changed priority from unflaired to flaired clones, which should now be the only type of clone to appear. (@MurdoMaclachlan)
- Allowed gracefully handling kill signals such as CTRL+C instead of instantly dying. (@MurdoMaclachlan)
- Prevented attempting to update or create a log file if the log is empty. (@MurdoMaclachlan)
- Prevented attempting to update post_list.txt if there are no changes from the last cycle. (@MurdoMaclachlan)
- Fixed a typo in the README. (@MurdoMaclachlan)

## 0.5.1

- Improved type hinting. (@MurdoMaclachlan)

## 0.5.0

As of this version, Python 3.5+ is required.

- Added type hinting. (@MurdoMaclachlan)
- Condensed some strings with fstrings. (@MurdoMaclachlan)
- Fixed a crash on encountering an unflaired post. (@MurdoMaclachlan)

## 0.4.0

- First public release.
- Switched to more object-oriented system for global variables. (@MurdoMaclachlan)
- Switched to array-based system for cleaner logging. (@MurdoMaclachlan)
- Many small optimisations. (@MurdoMaclachlan)
- Added commenting. (@MurdoMaclachlan)
- Added README and requirements.txt. (@MurdoMaclachlan)
- Fixed a crash when the data directory or cloneLog.txt file were missing. (@MurdoMaclachlan)