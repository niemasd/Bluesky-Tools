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
LIMIT_FEED = 10
POST_PREVIEW_LENGTH = 100

# convert a string to HTML-safe
def html_safe(s):
    if isinstance(s, str):
        char_map = [ # https://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references#List_of_character_entity_references_in_HTML
            ('&', '&amp;'),
            ('<', '&lt;'),
            ('>', '&gt;'),
        ]
        for k, v in char_map:
            s = s.replace(k, v)
    return s

# show error dialog
def error(error_message='An error occurred'):
    message_dialog(title='%s - ERROR' % TITLE, text=HTML("<ansired>ERROR:</ansired> %s" % error_message)).run()

# log into Bluesky
def login():
    client = None
    while client is None:
        username = input_dialog(title='%s - Login - Username' % TITLE, text=HTML("Please enter your Bluesky <ansired>username</ansired> (without the @):"), cancel_text="Exit").run()
        if username is None:
            return None
        password = input_dialog(title='%s - Login - Password' % TITLE, text=HTML("Please enter your Bluesky <ansired>password</ansired>:"), password=True).run()
        client = Client()
        try:
            client.login(username, password)
        except Exception as e:
            error(error_message="Unable to sign into Bluesky with provided credentials (username: <ansired>%s</ansired>)\n\n%s" % (username, e))
            client = None
    return client

# view a post: https://atproto.blue/en/latest/atproto/atproto_client.models.app.bsky.feed.defs.html#atproto_client.models.app.bsky.feed.defs.PostView
def view_post(client, post):
    text_items = [
        ('Author', html_safe('%s (%s)' % (post.author.handle, post.author.did))),
        ('Created', html_safe(post.record.created_at)),
        ('CID', html_safe(post.cid)),
        ('URI', html_safe(post.uri)),
        ('Number of Likes', html_safe(post.like_count)),
        ('Number of Replies', html_safe(post.reply_count)),
        ('Number of Reposts', html_safe(post.repost_count)),
        ('Number of Quotes', html_safe(post.quote_count)),
    ]
    text = "Viewing post by: <ansired>%s</ansired>\n\n%s" % (html_safe(post.author.handle), '\n'.join("- <ansiblue>%s:</ansiblue> %s" % tup for tup in text_items))
    text += "\n\n<ansiblue>Post Text</ansiblue>\n%s" % html_safe(post.record.text)
    if hasattr(post, 'embed') and post.embed is not None:
        text += "\n\n<ansiblue>Post Embed</ansiblue>\n"

        # https://atproto.blue/en/latest/atproto/atproto_client.models.app.bsky.embed.external.html#atproto_client.models.app.bsky.embed.external.View
        if post.embed.py_type == 'app.bsky.embed.external#view':
            embed_text_items = [
                ('Title', html_safe(post.embed.external.title)),
                ('Description', html_safe(post.embed.external.description)),
                ('URI', html_safe(post.embed.external.uri)),
            ]
            if post.embed.external.thumb is not None:
                embed_text_items.append(('Thumbnail', html_safe(post.embed.external.thumb)))
            text += '\n'.join("- <ansiblue>%s:</ansiblue> %s" % tup for tup in embed_text_items)

        # https://atproto.blue/en/latest/atproto/atproto_client.models.app.bsky.embed.images.html#atproto_client.models.app.bsky.embed.images.View
        elif post.embed.py_type == 'app.bsky.embed.images#view':
            for image_num, image in enumerate(post.embed.images):
                text += "- <ansiblue>Image %d:</ansiblue>\n" % (image_num + 1)
                image_text_items = [
                    ('Image URL', html_safe(image.fullsize)),
                    ('Thumbnail URL', html_safe(image.thumb)),
                    ('Alt Text', html_safe(image.alt)),
                ]
                text += '\n'.join("  - <ansiblue>%s:</ansiblue> %s" % tup for tup in image_text_items)

        # https://atproto.blue/en/latest/atproto/atproto_client.models.app.bsky.embed.record.html#atproto_client.models.app.bsky.embed.record.View
        elif post.embed.py_type == 'app.bsky.embed.record#view':
            embed_text_items = [
                ('Quoted Post Author', html_safe('%s (%s)' % (post.embed.record.author.handle, post.embed.record.author.did))),
                ('Quoted Post CID', html_safe(post.embed.record.cid)),
                ('Quoted Post URI', html_safe(post.embed.record.uri)),
            ]
            text += '\n'.join("- <ansiblue>%s:</ansiblue> %s" % tup for tup in embed_text_items)

        # unknown embed type
        else:
            text += "<ansired>Unsupported embed type: %s</ansired>" % html_safe(post.embed.py_type)
    message_dialog(title='%s - Post' % TITLE, text=HTML(text)).run()

# view the feed of a given Bluesky profile given a handle or DID
def view_profile_feed(client, username):
    profile = client.get_profile(username); cursors = [None]; curr_cursor_ind = 0
    while True:
        text = "Viewing feed of profile: <ansired>%s</ansired> (page %d)" % (html_safe(profile.handle), curr_cursor_ind+1)
        response = client.get_author_feed(username, limit=LIMIT_FEED, cursor=cursors[curr_cursor_ind])
        if (response.cursor is not None) and (curr_cursor_ind == (len(cursors) - 1)):
            cursors.append(response.cursor)
        values = list()
        if curr_cursor_ind != (len(cursors) - 1):
            values.append(('next', HTML("<ansigreen>=== Next ===</ansigreen>")))
        if curr_cursor_ind != 0:
            values.append(('prev', HTML("<ansiblue>=== Previous ===</ansiblue>")))
        for feed_post in response.feed:
            post = feed_post.post
            post_text = html_safe(post.record.text.replace('\n', ' '))
            if post.author.did != profile.did:
                post_text = "<ansired>[Repost %s]</ansired> %s" % (html_safe(post.author.handle), post_text)
            if len(post_text) > POST_PREVIEW_LENGTH:
                post_text = "%s<ansired>[...]</ansired>" % post_text[:POST_PREVIEW_LENGTH]
            values.append((post, HTML(post_text)))
        val = radiolist_dialog(title='%s - Posts - %s' % (TITLE, html_safe(profile.handle)), text=HTML(text), values=values).run()
        if val is None:
            return
        elif val == 'prev':
            curr_cursor_ind -= 1
        elif val == 'next':
            curr_cursor_ind += 1
        else:
            view_post(client, val)

# view a Bluesky profile given a handle or DID
def view_profile(client, username):
    while True:
        profile = client.get_profile(username)
        text_items = [ # https://atproto.blue/en/latest/atproto/atproto_client.models.app.bsky.actor.defs.html#atproto_client.models.app.bsky.actor.defs.ProfileViewDetailed
            ('Handle', html_safe(profile.handle)),
            ('DID', html_safe(profile.did)),
            ('Created', html_safe(profile.created_at)),
            ('Display Name', html_safe(profile.display_name)),
            ('Avatar URL', html_safe(profile.avatar)),
            ('Banner URL', html_safe(profile.banner)),
            ('Description', html_safe(profile.description)),
            ('Number of Followers', html_safe(profile.followers_count)),
            ('Number of Follows', html_safe(profile.follows_count)),
            ('Number of Posts', html_safe(profile.posts_count)),
        ]
        text = "Viewing profile: <ansired>%s</ansired>\n\n%s" % (html_safe(profile.handle), '\n'.join("- <ansiblue>%s:</ansiblue> %s" % tup for tup in text_items))
        values = [
            ('view_profile_feed', "View Profile Feed"),
        ]
        val = radiolist_dialog(title='%s - Profile - %s' % (TITLE, html_safe(profile.handle)), text=HTML(text), values=values).run()
        if val is None:
            return
        elif val == 'view_profile_feed':
            view_profile_feed(client, profile.did)
        else:
            raise ValueError("Invalid selection: %s" % val)

# search for and view a Bluesky profile using handle or DID
def search_profile(client):
    while True:
        username = input_dialog(title='%s - Search Profile' % TITLE, text=HTML("Please enter Bluesky <ansired>username</ansired> (without the @):")).run()
        if username is not None:
            try:
                view_profile(client, username)
            except:
                error(error_message="Username not found: <ansired>%s</ansired>\n\nPlease make sure to enter a valid Bluesky handle (without the @) or DID." % username)
                continue
        break

# Bluesky TUI home page
def home(client):
    while True:
        text_items = [
            ('Client Handle', html_safe(client._session.handle)),
            ('Client DID', html_safe(client._session.did)),
        ]
        text = '\n'.join("- <ansiblue>%s:</ansiblue> %s" % tup for tup in text_items)
        values = [
            ('view_client_profile', "View Client Profile"),
            ('search_profile', "Search for Profile"),
        ]
        val = radiolist_dialog(title='%s - Home - %s' % (TITLE, html_safe(profile.handle)), text=HTML(text), values=values, cancel_text="Exit").run()
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
