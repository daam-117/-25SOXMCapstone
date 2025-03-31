import sys
import csv
import re

sys.stdout.reconfigure(encoding='utf-8')

WORD_BANK = [
    "deep state", "fake news", "mainstream media", "woke agenda", "censorship", "freedom of speech",
    "patriot", "true patriot", "globalist", "elite control", "agenda 2030", "new world order", "groomers",
    "they don’t want you to know", "wake up, sheeple", "brainwashed masses", "shadow government",
    "controlled opposition", "liberal indoctrination", "they are lying to you", "follow the money",
    "secret cabal", "we are being silenced",
    "rigged election", "stolen votes", "ballot harvesting", "voter fraud", "mail-in fraud",
    "dominion machines", "stop the steal", "dead voters", "illegals voting",
    "civil war incoming", "the storm is coming", "time to rise up", "we need a revolution",
    "militia", "blood in the streets", "take back our country", "no more elections", "the great reset",
    "#maga", "#draintheswamp", "#stopthesteal", "#novaccinemandates", "#buildthewall",
    "#resistance", "#bluewave", "#abolishice", "#taxtherich", "#defundthepolice",
    "west is collapsing", "american decline", "china rising",
    "russia strong", "western propaganda", "imperialist lies","topnews", "politics", "trump", "biden", "harris", "clinton", "president"
]

WORD_BANK = [word.lower() for word in WORD_BANK]

input_file = "testFileLarge-25000.txt"
output_file = "filtered_tweets.txt"

with open(input_file, "r", encoding="utf-8", newline='') as f, open(output_file, "w", encoding="utf-8") as out_f:
    tweets = csv.reader(f)
    counter = 0
    matched_tweets = []

    for t in tweets:
        try:
            counter += 1
            tweetID = t[1]  # Tweet ID
            tweetText = t[2]  


            user_data = t[3]
            match = re.search(r"'screen_name': '([^']+)'", user_data)
            tweetUser = match.group(1) if match else "Unknown"

            description_match = re.search(r"'description': '([^']+)'", user_data)
            profileDescription = description_match.group(1) if description_match else "No description"


            tweet_lower = tweetText.lower()
            description_lower = profileDescription.lower()
            
            if any(word in tweet_lower or word in description_lower for word in WORD_BANK):
                matched_tweets.append((tweetID, tweetUser, tweetText, profileDescription))

        except IndexError:
            print("Skipping a malformed entry...")


    for tweet in matched_tweets:
        out_f.write("=" * 50 + "\n")
        out_f.write(f"Tweet ID: {tweet[0]}\n")
        out_f.write(f"Username: {tweet[1]}\n")
        out_f.write(f"Tweet Content: {tweet[2]}\n")
        out_f.write(f"Profile Description: {tweet[3]}\n")
        out_f.write("=" * 50 + "\n\n")

print(f"\nTotal Matched Tweets: {len(matched_tweets)}")
print(f"Filtered tweets have been saved to {output_file}")
