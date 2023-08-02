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
- `save_saved_posts`: Whether to save all posts that the specified user has saved. Note: This requires obtaining a cookie and adding it to the `cookie` field below.
- `save_saved_comments`: Whether to save all comments that the specified user has saved. This also requires a `cookie`.

If you want to archive saved posts and comments, you will have to specify a token for authentification:

- `cookie`: Put your `reddit_session` cookie here to access reddit pages which require authentication. See the below guide on how to obtain it.

### Obtaining your Reddit (session-)token

To access saved posts and comments, you will have to obtain a cookie of your Reddit session. This is only needed if you want to archive saved posts and comments. If you get a 403 error, you are most likely using the wrong token. Make sure to keep this token safe, as anyone who has the token has full access to your Reddit account. If you believe your token has been compromised, logging out of the browser which the token was extracted from *should* invalidate the token.

1. In your web browser, navigate to the Reddit website and log in with your Reddit account credentials if you haven't already done so.
2. Once logged in, open the developer tools in your web browser. You can usually do this by right-clicking on any part of the webpage and selecting "Inspect" or "Inspect Element". In Firefox they can also be opened by pressing `F12`.
3. In the developer tools panel, navigate to the "Network" tab. This tab will show all the network requests and responses made by the webpage.
4. Now, go to the [json of the Reddit homepage](https://www.reddit.com/.json) or any other json Reddit page that uses authentication, such as your user profile or saved posts, by adding `.json` to the end of the URL.
5. In the network tab, you should see a request with Status 200 and File .json. Click on the request to view its details. In the "Headers" section, look for the "Request Headers" subsection.
6. In the "Request Headers," find the line that starts with "Cookie". This line contains your session's authentication token (usually named "reddit_session").
   Example `Cookie` value: `rdt=...; edgebucket=...; token_v2=.........; g_state={...}; reddit_session=YOUR_AUTHENTICATION_TOKEN; eu_cookie={...}; pc=...; session_tracker=......`
7. Copy the value of reddit_session. It will look something like this: reddit_session=YOUR_AUTHENTICATION_TOKEN. The token's last character is the one before the semicolon.
8. Now, open the Python script in a text editor again and locate the cookie field in the settings section. Set its value to the authentication token you copied in the previous step. The line should look like this: `cookie = "YOUR_AUTHENTICATION_TOKEN"`

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
