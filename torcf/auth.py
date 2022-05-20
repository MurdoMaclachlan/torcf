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

import praw
import socket
import sys
import webbrowser
from configparser import NoSectionError
from praw.exceptions import MissingRequiredAttributeException
from random import randint
from typing import Dict
from .creds import add_refresh_token, create_credentials, get_credentials
from .globals import Globals
from .logger import Log

global Globals, Log


def check_failure(client: object, params: Dict, state: str) -> None:
    """Checks for an authorisation failure, either due to a state mismatch or Reddit
    throwing an error in the return parameters.

    Arguments:
    - client (object)
    - params (dictionary)
    - state (string)

    No return value.
    """
    if state != params["state"]:
        message = f"State mismatch. Expected: {state} - Received: {params['state']}"
        send_message(client, message)
        Log.new(message, "FATAL")
        sys.exit()
    elif "error" in params:
        send_message(client, params["error"])
        Log.new([params["error"]], "FATAL")
        sys.exit()


def init() -> object:
    """Initialises the Reddit instance, creating a new praw.ini if none is found.

    No arguments.

    Returns: praw.Reddit instance.
    """
    try:
        return login()
    # Catch for invalid praw.ini, will create a new one then restart the program; the
    # restart is required due to current PRAW limitations. :'(
    except (NoSectionError, MissingRequiredAttributeException, KeyError):
        if create_credentials():
            Log.new(
                "praw.ini successfully created, program restart required for this"
                + " to take effect.",
                "INFO"
            )
        else:
            Log.new("Failed to create praw.ini file, something went wrong.", "WARNING")
        sys.exit()


def login() -> object:
    """Handles the Reddit login and authorisation using credentials from praw.ini; will
    also handle initial refresh token setup if 2FA is enabled for the account.

    No arguments.

    Returns: praw.Reddit instance.
    """
    creds = get_credentials()

    constants = {
        "user_agent": f"{sys.platform}:tcf:v{Globals.VERSION}:by /u/MurdoMaclachlan",
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "username": creds["username"],
    }

    # Indicates user will not have authorised TCF yet
    if "refresh_token" not in creds.keys():
        reddit = praw.Reddit(redirect_uri=creds["redirect_uri"], **constants)
        state = str(randint(0, 65000))
        scopes = ["edit", "history", "modlog", "modposts", "read"]
        url = reddit.auth.url(scopes, state, "permanent")
        Log.new(
            "TCF has not yet been authorised with your account. The program"
            + " will now open a tab in your browser to complete this process.",
            "INFO"
        )
        webbrowser.open(url)

        client = receive_connection()
        data = client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {
            key:
            value for (key, value) in [
                token.split("=") for token in param_tokens
            ]
        }

        # Check for an authorisation failure
        check_failure(client, params, state)

        refresh_token = reddit.auth.authorize(params["code"])
        add_refresh_token(creds, refresh_token)
        send_message(
            client,
            f"Refresh token: {refresh_token}. Feel free to close"
            + " this page. This message is simply for success"
            + " confirmation; it is not necessary to save your"
            + " refresh_token, as TCF has automatically done this.",
        )
    # If user has already authorised TCF
    else:
        reddit = praw.Reddit(refresh_token=creds["refresh_token"], **constants)

    return reddit


def receive_connection() -> object:
    """Wait for and then return a connected socket. Opens a TCP connection on port 8080,
    and waits for a single client.

    No arguments.

    Returns: client object.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client: object, message: str) -> None:
    """Sends a message to the client and closes the connection.

    Arguments:
    - client (object)
    - message (string)

    No return value.
    """
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()