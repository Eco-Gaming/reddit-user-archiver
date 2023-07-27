import os
import requests
import time
import json

# Settings
username = "your-username-here" # reddit username
delay = 5 # delay between requests (in seconds)
delay_after_rate_limit = 600 # time to wait before next request if rate-limit is encountered (in seconds)
rate_limit_retry_limit = 5 # how many times to retry request after being rate-limited, set this to -1 to infinitely retry
duplicate_posts = False # save users posts that also have users comments in posts and comments folder?

save_posts = True
save_comments = True
save_saved_posts = False
save_saved_comments = False

# Other variables (these do not have to be changed)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
# headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'}
urls = set() # Set to store post URLs and check for duplicates (useful for comment archiving)
failed_urls = [] # downloads that failed once


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def save_post_as_json(post_data_json, folder_path, filename):
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        # File does not exist, so save the data with the original filename
        with open(file_path, 'w') as f:
            json.dump(post_data_json, f, indent=4)
    else:
        # File with the same name already exists, find a new filename
        base_name, extension = os.path.splitext(filename)
        i = 1
        while True:
            new_filename = f"{base_name}_{i}{extension}"
            new_file_path = os.path.join(folder_path, new_filename)
            if not os.path.exists(new_file_path):
                # Save the data with the new filename
                with open(new_file_path, 'w') as f:
                    json.dump(post_data_json, f, indent=4)
                break
            i += 1

def save_post(post_url, base_folder, subreddit, delay, retry=0):
    folder_path = os.path.join(base_folder, subreddit)
    create_folder_if_not_exists(folder_path)

    # Introduce a delay between requests to avoid rate-limiting
    time.sleep(delay)

    try:
        post_response = requests.get(post_url, headers=headers)
        if post_response.status_code == 200:
            post_data = post_response.json()
            post = post_data[0]['data']['children'][0]['data']
            title = post['title']
            author = post['author']
            if len(title) > 50:
                post_filename = f"{author}_{title[0:50]}"
            else:
                post_filename = f"{author}_{title}"
            # Remove any characters that are not allowed in filenames
            post_filename = ''.join(c if c.isalnum() else '_' for c in post_filename)
            post_filename += ".json"
            save_post_as_json(post_data, folder_path, post_filename)
            print(f"'{title}' from {subreddit} saved successfully!")
            return True
        else:
            if post_response.status_code == 429 and (retry < rate_limit_retry_limit or rate_limit_retry_limit == -1):
                print(f"You are being rate-limited (Response Code 429). Waiting {delay_after_rate_limit} seconds before continuing...")
                time.sleep(delay_after_rate_limit)
                return save_post(post_url, base_folder, subreddit, delay, retry+1)

            elif post_response.status_code == 429:
                print(f"The previous request failed due to rate-limiting, it will be retried later (max retries reached).")
            else:
                print(f"Failed to fetch post details. Response Code: {post_response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching post details: {str(e)}")

    return False

def retry_failed_downloads(failed_downloads):
    print("Retrying failed downloads...")
    retry_fail_downloads = []
    for post_url, base_folder, subreddit, delay in failed_downloads:
        if not save_post(post_url, base_folder, subreddit, delay):
            retry_fail_downloads.append((post_url, base_folder, subreddit, delay))

    retry_fail_downloads_length = len(retry_failed_downloads)

    print(f"The following {retry_fail_downloads_length} download(s) failed:")
    for post_url, base_folder, subreddit, delay in retry_fail_downloads:
        print(f"{post_url}")

    print("You can attempt to manually download these by visiting the above links.")

    return retry_fail_downloads

def archive_user_posts(username, delay):
    base_url = f"https://old.reddit.com/user/{username}/submitted.json"

    after = None
    terminatable = False
    retry = 0

    print("Archiving posts...")

    while True:
        url = base_url

        if after:
            url = f"{base_url}?after={after}"
            terminatable = True

            # Introduce a delay between requests to avoid rate-limiting
            time.sleep(delay)

        elif terminatable:
            print("All posts archived.")
            break

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'children' in data['data']:
                posts = data['data']['children']
                if not posts:
                    print("No more posts to fetch.")
                    break

                for post in posts:
                    post_data = post['data']
                    subreddit = post_data['subreddit']
                    post_permalink = post_data['permalink']
                    post_url = f"https://old.reddit.com{post_permalink}.json"

                    if post_url not in urls:
                        if save_post(post_url, "posts", subreddit, delay):
                            urls.add(post_url)
                        else:
                            failed_urls.append((post_url, "posts", subreddit, delay))

                after = data['data']['after']
            else:
                print("No posts found for the user.")
                break
        elif response.status_code == 429 and (retry < rate_limit_retry_limit or rate_limit_retry_limit == -1):
            print(f"You are being rate-limited (Response Code 429). Waiting {delay_after_rate_limit} seconds before continuing...")
            time.sleep(delay_after_rate_limit-delay)
        elif response.status_code == 429:
            print(f"The previous request failed due to rate-limiting. Aborting... (max retries reached).")
            break
        else:
            print(f"Failed to fetch data. Response Code: {response.status_code}. Please check the username and try again.")
            break

def archive_user_comments(username, delay):
    base_url = f"https://old.reddit.com/user/{username}/comments.json"

    if duplicate_posts:
        urls.clear()

    after = None
    terminatable = False
    retry = 0

    print("Archiving comments...")

    while True:
        url = base_url

        if after:
            url = f"{base_url}?after={after}"
            terminatable = True

            # Introduce a delay between requests to avoid rate-limiting
            time.sleep(delay)

        elif terminatable:
            print("All comments archived.")
            break

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'children' in data['data']:
                comments = data['data']['children']
                if not comments:
                    print("No more comments to fetch.")
                    break

                for comment in comments:
                    comment_data = comment['data']
                    link_permalink = comment_data['link_permalink']
                    comment_url = f"{link_permalink}.json"
                    subreddit = comment_data['subreddit']

                    if comment_url not in urls:
                        if save_post(comment_url, "comments", subreddit, delay):
                            urls.add(comment_url)
                        else:
                            failed_urls.append((comment_url, "comments", subreddit, delay))

                after = data['data']['after']
            else:
                print("No comments found for the user.")
                break
        elif response.status_code == 429 and (retry < rate_limit_retry_limit or rate_limit_retry_limit == -1):
            print(f"You are being rate-limited (Response Code 429). Waiting {delay_after_rate_limit} seconds before continuing...")
            time.sleep(delay_after_rate_limit-delay)
        elif response.status_code == 429:
            print(f"The previous request failed due to rate-limiting. Aborting... (max retries reached).")
            break
        else:
            print(f"Failed to fetch data. Response Code: {response.status_code}. Please check the username and try again.")
            break

if __name__ == "__main__":
    if save_posts:
        archive_user_posts(username, delay)
        print()
    if save_comments:
        archive_user_comments(username, delay)
        print()

    retry_failed_downloads(failed_urls)
