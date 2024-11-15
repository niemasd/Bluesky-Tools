This repository contains a collection of tools I wrote to automate various tasks via the Bluesky API.

* **[`follower_enrichment.py`](follower_enrichment.py)** - Given a set of Bluesky accounts *A*, sort the union of their followers *F* in descending order of "enrichment," defined using one of the following metrics:
  * `count` - The "enrichment score" of follower *f* in *F* is the number of accounts in *A* that *f* follows
  * `proportion` - The "enrichment score" of follower *f* in *F* is the number of accounts in *A* that *f* follows (i.e., `count`) divided by the total number of accounts followed by *f*
