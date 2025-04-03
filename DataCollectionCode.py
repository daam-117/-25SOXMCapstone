import re
import pandas as pd
import gspread
from openai import OpenAI
from oauth2client.service_account import ServiceAccountCredentials

# Initialize OpenAI client
client = OpenAI(api_key='OpenAPIKey')

# Default generation settings (editable)
temperature = 0.7
top_p = 1.0
frequency_penalty = 0.0
presence_penalty = 0.0

# Load text file and extract tweets
def extract_tweets(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    tweets = re.findall(r"Tweet Content: b'(.*?)'", content)
    cleaned_tweets = [tweet.replace("\\n", " ").replace("\\xe2\\x80\\xa6", "...") for tweet in tweets]
    return cleaned_tweets

# Prompt variations
prompts = {
    "Brainstorm": (
        "You are an expert in behavioral manipulation of people through the use of email and social media for Influence campaigns by adversaries such as Russia, China, Iran, or North Korea. "
        "You understand that news, advertising, and other information is often presented in ways to maximize engagement, and are able to distinguish between legitimate and malicious manipulation. "
        "Examine the following post to determine if it might be manipulating the reader to believe something that is not true through psychological information tactics or targeted misinformation campaigns. "
        "If the post fits into one of those categories, describe why in less than two sentences. If it is a part of an influence campaign, begin with 'YES'. If it is not, then begin with 'NO'. "
        "Post: {{tweet}}"
    ),
    "ImprovedBrainstorm": (
        "You are an expert in behavioral manipulation of people through the use of email and social media for Influence campaigns by adversaries such as Russia, China, Iran, or North Korea. "
        "You understand that news, advertising, and other information is often presented in ways to maximize engagement, and are able to distinguish between legitimate and malicious manipulation. "
        "Examine the following post to determine if it might be manipulating the reader to believe something that is not true through psychological information tactics or targeted misinformation campaigns. "
        "Also keep in mind that trusted sources such as the president, trusted and verified American news sources, and other trusted American celebrity/social media influencer/well-known twitter accounts with many followers are more than likely to not be a part of influence campaigns by an adversarial country. "
        "If the post fits into one of those categories, describe why in less than two sentences. If it is a part of an influence campaign, begin with 'YES'. If it is not, then begin with 'NO'. "
        "Post: {{tweet}}"
    ),
    "Simple": (
        "You are a disinformation analyst. Does the following post use psychological or manipulative tactics that are characteristic of influence campaigns from countries like Russia, China, Iran, or North Korea? "
        "Respond with 'YES' or 'NO' followed by a short explanation. Post: {{tweet}}"
    ),
    "OpenAIPrompt": (
        "You are a geopolitical influence operations analyst trained in identifying psychological manipulation and disinformation campaigns across social media platforms. "
        "You specialize in detecting covert influence efforts from adversarial states such as Russia, China, Iran, and North Korea. "
        "Your mission is to analyze online content (especially tweets) and determine whether the message attempts to manipulate public opinion, spread disinformation, or psychologically influence readers. "
        "You are especially attentive to: language that appeals to fear, anger, nationalism, or tribal identity; messages that misrepresent facts or omit key context; and attempts to sow division, distrust in institutions, or promote hostile foreign narratives. "
        "Please follow these steps: 1) Analyze the content carefully. 2) Determine whether the post shows signs of influence operations or psychological manipulation. "
        "3) If YES, begin your response with 'YES' and briefly (in ≤2 sentences) explain the manipulation tactic. 4) If NO, begin your response with 'NO' and briefly explain why it seems innocuous or legitimate. "
        "Here is the post to evaluate: {{tweet}}"
    )
}

# Models to compare
models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]

# Analyze tweet
def analyze_tweet(tweet_text, model_name, prompt_template):
    prompt = prompt_template.replace("{{tweet}}", tweet_text)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": prompt}]
    )
    response_text = response.choices[0].message.content.strip()
    response_prefix = response_text[:3].upper() if response_text else "NO"
    is_influence = "YES" if response_prefix == "YES" else "NO"
    return response_text, is_influence

# Extract tweets
file_path = "/home/vboxuser/myenv/capstonecode/2016test.txt"
tweets = extract_tweets(file_path)

# Collect results
results = []
for model_name in models:
    for prompt_name, prompt_text in prompts.items():
        for tweet in tweets:
            response, is_influence = analyze_tweet(tweet, model_name, prompt_text)
            results.append([model_name, prompt_name, tweet, response, is_influence])

# Create output DataFrame
output_df = pd.DataFrame(results, columns=['Model', 'Prompt Version', 'Tweet Text', 'OpenAI Response', 'Influence Mark'])

# Generate summary statistics
summary_df = (
    output_df.groupby(['Model', 'Prompt Version', 'Influence Mark'])
    .size().unstack(fill_value=0).reset_index()
)
summary_df['Total'] = summary_df['YES'] + summary_df['NO']
summary_df['% YES'] = (summary_df['YES'] / summary_df['Total']) * 100

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/home/vboxuser/myenv/capstonecode/soxmkey.json", scope)
gs_client = gspread.authorize(creds)

# Upload to Google Sheets
gsheet = gs_client.create("Influence Prompt+Model Comparison")
gsheet.share('xaviermjames@gmail.com', perm_type='user', role='writer')

worksheet = gsheet.get_worksheet(0)
worksheet.update([output_df.columns.values.tolist()] + output_df.values.tolist())

summary_ws = gsheet.add_worksheet(title="Summary", rows="50", cols="10")
summary_ws.update([summary_df.columns.values.tolist()] + summary_df.astype(str).values.tolist())

print("Analysis complete. Results and summary uploaded to Google Sheets.")