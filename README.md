# witbanner

Provides easy programmatic access to LeopardWeb.

* To install: `pip install -r requirements.txt`
* See/run top-level files for example recipes

## Technical Details
* Initialization (`banner.init`) can come from interactive login (no argument) or a "session id" supplied by Banner. This can be retrieved at the end of a prior run (`banner.lastid()`) or by looking at the `SESSID` cookie (`chrome://settings/cookies` -> `prodweb2.wit.edu`) of a fresh load (i.e. immediately after accessing `leopardweb.wit.edu` in a browser).
