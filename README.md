# TCF (ToR Clone Finder)

**This is an UNOFFICIAL tool. It has been helpful to me in identifying clones in the past, so I thought I would share it for others.**

This small tool finds, notifies and documents cloned posts in r/TranscribersOfReddit queue. These clones arise as a result of Reddit sending an error response despite there actually being no error, causing the bot to attempt to post again and resulting in a clone appearing.

Most clones are easy to identify; they have no flair and all link to the same partner post. This type of clone is caused by Reddit erroring during the flairing part of post creation, forcing Blossom to re-submit from the top. Generally here, the final post to be submitted will be the successful, flaired one. I call this type of clone a "Soft Clone".

The second, far rarer type of clone, which I call a "Hard Clone", does have a flair. In this instance, it's uncertain where the error ocurred, but it is likely that Reddit errored at some point following the flairing of the post. This case is harder to deal with, so TCF has no built-in ability to remove these, and instead requests manual action.

## Using this tool

Being a program I wrote originally for personal use, this program does not have anything built in for editing config or setting up praw.ini. The process for setting it up is very simple; it enforces the use of refresh tokens, so simply create an app for it, copy in the client id and secret and your username, and it will guide you through the remainder of the authentication process. 

Config is done through a simple run-time argument system. When you run the `clone_finder` script in the terminal, you can pass the following options:

- `--check` or `-c`; tells TCF to check for any posts from a list of partner subs (which it will prompt you to enter), keeping a log of their link and current flair in `post_list.txt`, in the data folder.
- `--remove` or `-r`; tells TCF to remove any soft clones it finds. Note that this will crash your program if you do not have moderator permissions. Even if you do have moderator permissions, it is **not recommended to set this as True** until further testing is done to make sure non-clones are not accidentally removed.
- `--verbose`, or `-v`; tells TCF to send a desktop notification whenever it skips a cycle.
- `--wait` or `-w`; allows you to enter a custom number of seconds for TCF to wait between cycles. The number should be given immediately succeeding the argument, separated by a single space, like so: `--wait 60`. The default wait time, if TCF cannot parse the argument or it is not passed, is 30 seconds.

Requirements for installing the program can be found in `requirements.txt`. The program requires a minimum Python version of **3.5** due to the use type hinting. The default praw.ini section header is `tcf` (ToR Clone Finder) but this can be changed.

The program's data, including the `praw.ini` file and any logs, is stored in a subfolder of the working directory (the directory it is run from). I suggest creating a folder specifically for the program; mine is stored in a `programs/clone_finder` subfolder of my Transcribers of Reddit-related folder.
