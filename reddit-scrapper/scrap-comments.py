import praw, json

reddit = praw.Reddit(client_id="_CLIENT_ID_",
                     client_secret="_CLIENT_SECRET_",
                     password="_PASSWORD_",
                     user_agent="taiwanchatbot",
                     username="_USERNAME_")

with open('comments.json', 'w') as outfile:

    for submission in reddit.subreddit("taiwan").search(query="weekly+discussion+%26+questions+thread", sort='new'):
        for top_level_comment in submission.comments:
            if top_level_comment.body == "[deleted]" or top_level_comment.body == "[removed]":
                continue
            print("========================")
            print(top_level_comment.body)
            json.dump(top_level_comment.body, outfile)
            outfile.write(top_level_comment.body)
            outfile.write('\n')
            print("========================")
