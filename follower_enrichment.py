#! /usr/bin/env python3
'''
Find enriched followers of a group of accounts
'''

# imports
from getpass import getpass
from sys import stderr
import argparse
try:
    from atproto import Client
    import atproto_client
except:
    raise RuntimeError("Missing Python package `atproto`. Install it: pip install atproto")

# print to log
def print_log(s='', end='\n'):
    stderr.write(s); stderr.write(end); stderr.flush()

# get all of the profiles of a large list of handles
def get_profiles(handles, client):
    MAX_LEN = 25 # because of error: 'List should have at most 25 items after validation'
    handles = list(set(handles))
    profiles = list()
    for i in range(0, len(handles), MAX_LEN):
        print_log("Loaded %d of %d profiles..." % (i, len(handles)))
        profiles += client.get_profiles(handles[i:i+MAX_LEN]).profiles
    return profiles

# enrichment = number of given users being followed
def metric_count(followers, client):
    return {follower_account:sum(1 for k in followers if follower_account in followers[k]) for account, account_followers in followers.items() for follower_account in account_followers}

# enrichment = proportion of given users being followed (i.e., count divided by total follows)
def metric_proportion(followers, client):
    scores = metric_count(followers, client)
    follower_profiles = get_profiles(list(scores.keys()), client)
    follows_count = {follower_profile.handle.strip() : follower_profile.follows_count for follower_profile in follower_profiles}
    for k in scores:
        if k not in follows_count:
            raise RuntimeError("Missing follows count: %s" % k)
        scores[k] /= follows_count[k]
    return scores

# enrichment metrics mapping
METRICS = {
    'count': metric_count,
    'proportion': metric_proportion,
}

# parse user arguments
def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--metric', type=str, default='count', help="Enrichment Metric")
    parser.add_argument('account', nargs='+', type=str, help="BlueSky Account")
    args = parser.parse_args()
    args.metric = args.metric.strip().lower()
    if args.metric not in METRICS:
        raise ValueError("Invalid enrichment metric: %s. Options: %s" % (args.metric, ' '.join(sorted(METRICS.keys()))))
    args.account = sorted({account.strip().lstrip('@').strip() for account in args.account})
    return args

# create Bluesky session
def create_session():
    print_log("Enter your Bluesky username: ", end='')
    username = input('').strip()
    print_log("Enter your Bluesky password: ", end='')
    password = getpass('').strip()
    client = Client()
    try:
        client.login(username, password)
    except Exception as e:
        print("ERROR: Failed to sign in. Please check username (should be the full domain, e.g. xyz.bsky.social) and password, and please disable 2FA.")
        raise e
    return client

# get followers of a Bluesky account
def get_followers(usernames, client):
    if isinstance(usernames, str):
        usernames = [usernames]
    graph = atproto_client.namespaces.sync_ns.AppBskyGraphNamespace(client)
    followers = dict()
    for username in usernames:
        print_log("Loading followers (%s)..." % username, end='')
        params = atproto_client.models.app.bsky.graph.get_followers.Params(actor=username, limit=100, cursor=None)
        response = graph.get_followers(params)
        curr_followers = {profile_view.handle.strip() for profile_view in response.followers}
        while response.cursor is not None:
            print_log('.', end='')
            params = atproto_client.models.app.bsky.graph.get_followers.Params(actor=username, limit=100, cursor=response.cursor)
            response = graph.get_followers(params)
            curr_followers |= {profile_view.handle.strip() for profile_view in response.followers}
        print_log()
        curr_followers.discard('handle.invalid')
        followers[username] = curr_followers
    return followers

# main program
def main():
    args = parse_args()
    print_log("Creating Bluesky session...")
    client = create_session()
    print_log("Loading followers...")
    followers = get_followers(args.account, client)
    scores = METRICS[args.metric](followers, client)
    print("Username\tScore (%s)" % args.metric)
    for username in sorted(scores.keys(), reverse=True, key=lambda x: (scores[x],x)):
        print("%s\t%s" % (username, scores[username]))

# run tool
if __name__ == "__main__":
    main()
