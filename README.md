This repository contains a collection of scripts I wrote to automate various tasks via the Bluesky API. Note that all scripts will require Bluesky username + password authentication, and 2FA must be disabled (if someone can figure out how to use the Python API with 2FA, let me know, and I can update my scripts).

* **[`follower_enrichment.py`](follower_enrichment.py)** - Given a set of Bluesky accounts *A*, sort the union of their followers *F* in descending order of "enrichment," defined using one of the following metrics:
  * `count` - The "enrichment score" of follower *f* in *F* is the number of accounts in *A* that *f* follows
  * `proportion` - The "enrichment score" of follower *f* in *F* is the number of accounts in *A* that *f* follows (i.e., `count`) divided by the total number of accounts followed by *f*
