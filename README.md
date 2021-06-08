# Clone Finder

**This is an UNOFFICIAL tool. It has been helpful to me in identifying clones in the past, so I thought I would share it for others.**

This small tool finds, notifies and documents cloned posts in r/TranscribersOfReddit queue. These clones arise as a result of Reddit sending an error response despite there actually being no error, causing the bot to attempt to post again and resulting in a clone appearing.

Clones are easy to identify, as they have no flair and will have the exact same title and link as the post before them. This program simply does it automatically, and logs info about it.

## Using this tool

Being a program I wrote originally for personal use, this program does not have anything built in for editing config or setting up praw.ini. The process for setting it up is the same as any other normal Reddit app. To edit config options, simply change the values hardcoded into the program.

The config options are:

- `Globals.DEBUG`; set to False by default. This will give log output for every post it checks, showing which ones it is skipping.
- `Globals.VERBOSE`; set to False by default. This give a desktop notification whenever it skips a cycle.
- `Globals.WAIT`; set to 30 by default. This is the number of seconds with the program waits between cycles.

Requirements for installing the program can be found in `requirements.txt`. The program requires a minimum Python version of **3.5** due to the use type hinting. The default praw.ini section header is `tcf` (ToR Clone Finder) but this can be changed.

The program uses `gi.repository.Notify` to give desktop notifications, thus requiring GTK+ 3. This should be available for Windows, macOS and all Unix-like systems.

The program's data is stored in a subfolder of the working directory (the directory it is run from). I suggest creating a folder specifically for the program; mine is stored in a `programs/clone_finder` subfolder of my Transcribers of Reddit-related folder.
