#! /usr/bin/env python3
'''
Terminal User Interface (TUI) for Bluesky
'''

# imports
try:
    from atproto import Client
    import atproto_client
except:
    raise RuntimeError("Missing Python package `atproto`. Install it: pip install atproto")
try:
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.shortcuts import input_dialog, message_dialog, radiolist_dialog
except:
    raise RuntimeError("Missing Python package 'prompt_toolkit'. Install it: pip install prompt_toolkit")

# constants
VERSION = '0.0.1'
TITLE = 'Bluesky TUI v%s' % VERSION

# show error dialog
def error(title=TITLE, error_message='An error occurred'):
    message_dialog(title=title, text=HTML("<ansired>ERROR:</ansired> %s" % error_message)).run()

# log into Bluesky
def login(title=TITLE):
    client = None
    while client is None:
        username = input_dialog(title=title, text=HTML("Please enter your Bluesky <ansired>username</ansired>:"), cancel_text="Exit").run()
        if username is None:
            return None
        password = input_dialog(title=title, text=HTML("Please enter your Bluesky <ansired>password</ansired>:"), password=True).run()
        client = Client()
        try:
            client.login(username, password)
        except:
            error(title=title, error_message="Unable to sign into Bluesky with provided credentials (username: <ansired>%s</ansired>)" % username)
            client = None
    return client

# view a Bluesky profile given a handle or DID
def view_profile(client, username, title=TITLE):
    profile = client.get_profile(username)
    text_items = [ # https://atproto.blue/en/latest/atproto/atproto_client.models.app.bsky.actor.defs.html#atproto_client.models.app.bsky.actor.defs.ProfileViewDetailed
        ('Handle', profile.handle),
        ('DID', profile.did),
        ('Display Name', profile.display_name),
    ]
    text = '\n'.join("- <ansiblue>%s:</ansiblue> %s" % tup for tup in text_items)
    message_dialog(title=title, text=HTML(text)).run()

# search for and view a Bluesky profile using handle or DID
def search_profile(client, title=TITLE):
    username = input_dialog(title=title, text=HTML("Please enter Bluesky <ansired>username</ansired>:")).run()
    view_profile(client, username)

# Bluesky TUI home page
def home(client, title=TITLE):
    while True:
        text_items = [
            ('Client Handle', client._session.handle),
            ('Client DID', client._session.did),
        ]
        text = '\n'.join("- <ansiblue>%s:</ansiblue> %s" % tup for tup in text_items)
        values = [
            ('view_client_profile', "View Client Profile"),
            ('search_profile', "Search for Profile"),
        ]
        val = radiolist_dialog(title=title, values=values, text=HTML(text), cancel_text="Exit").run()
        if val is None:
            return
        elif val == 'view_client_profile':
            view_profile(client, client._session.did)
        elif val == 'search_profile':
            search_profile(client)
        else:
            raise ValueError("Invalid selection: %s" % val)

# main program
def main():
    client = login()
    if client is None:
        return
    home(client)

# run tool
if __name__ == "__main__":
    main()
