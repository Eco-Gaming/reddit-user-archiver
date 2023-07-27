# reddit-user-archiver

This is a tool created to easily archive a Reddit user's posts and comments in JSON format. It leverages Reddit's JSON data feeds to collect the data, producing JSON files that are identical to the ones provided by Reddit directly (for example: https://www.reddit.com/r/MuseumOfReddit/comments/ke8skw/the_poop_knife.json). It will not download any media files.

The archived json files can be viewed by modifying reddit json readers such as [geddit-app](https://github.com/kaangiray26/geddit-app) to accept local files. (There are probably more, I didn't look around yet).

Note: The majority of the code snippets in this project are adapted from ChatGPT.

## Usage

Before running the script, first open it in a text editor and set the settings at the top to the correct values:

- `username`: Replace `your-username-here` with the username of the reddit user you want to archive.
- `delay`: This is the delay between requests, it can be left at the default vaule of 5 seconds.
- `delay_after_rate_limit`: This determines how long the script will wait if it encounters a rate-limit error. This should also be fine at the default value of 600 seconds (10 minutes).
- `rate_limit_retry_limit`: How many times to retry a request if the previous one was rate-limited. Set to `-1` to infinitely retry.
- `duplicate_posts`: Change this value to `True` if you want to save your posts which also have at least one comment from you in both the posts and comments folder or leave it at `False` to only save them in the posts folder (This only has any effects when both posts and comments are being archived).

Underneath the main settings are a few options for what to archive:

- `save_posts`: Whether to save all the specified users posts.
- `save_comments`: Whether to save all posts that the specified user has commented on.

The other two options don't work yet, so leave them at `False` (changing them has no effect).

<hr>

The script can then be run by using the following command:
~~~
python reddit-user-archiver.py
~~~
The script will start archiving the user's posts and comments. The data will be stored in separate JSON files, organized by subreddit, within the posts and comments folders.

## Roadmap

Please note that the following tasks are listed in no specific order, and it is unlikely that I will work on them in the immediate future.

- code cleanup (move posts and comments into same method)
- option whether to save deleted posts
- continue from local files without re-downloading everything
- save media
- add auth
- add saving of saved posts and comments
