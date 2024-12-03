This repository contains a collection of scripts I wrote to automate various tasks via the Bluesky API. Note that all scripts will require Bluesky username + password authentication: if you have 2FA enabled on your account, you will need to create an [App Password](https://bsky.app/settings/app-passwords) to use instead of your main account password.

* **[`follower_enrichment.py`](follower_enrichment.py)** - Given a set of Bluesky accounts *A*, sort the union of their followers *F* in descending order of "enrichment," defined using one of the following metrics:
  * `count` - The "enrichment score" of follower *f* in *F* is the number of accounts in *A* that *f* follows
  * `proportion` - The "enrichment score" of follower *f* in *F* is the number of accounts in *A* that *f* follows (i.e., `count`) divided by the total number of accounts followed by *f*
* **[`tui_client.py`](tui_client.py)** - A [Terminal User Interface (TUI)](https://en.wikipedia.org/wiki/Text-based_user_interface) client for Bluesky
