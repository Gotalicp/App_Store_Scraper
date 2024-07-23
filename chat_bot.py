import pandas as pd
from summarizer import summarize
from nltk.tokenize import sent_tokenize


df = pd.ExcelFile('app_reviews.xlsx').parse('NBC News Breaking News & Live')
# reviews=["Real News",
#          "won't unlock",
#          "This was my go to news app until it started asking me to sign in with my email to read news stories. I uninstalled it yesterday and installed Epoch Times. I had the Fox News app for years.",
#          "No matter how many times I had the link sent and clicked on the link the app repeatedly told me the link has expired.",
#          "This was my go to source for News. Now with email and of course term and service agreement. I will start using CNN for my News.",
#          "HELLOOOOOO....anybody home? I have refreshed, un-installed and continue to contact you...and still I cannot comment on the stories here on FOX. It continually tells me there is an error and I should refresh the page. I'm tired of being nice. WHAT IDIOT IS MINDING THE STORE?? FIX THIS!! I can't comment on the stories anymore...first I have to sign up, then I receive an error. This has been going on for a long time...when are you going to fix it...or maybe you don't want my opinion...",
#         "Simply the worst app on the market",
#         "The pop up adds are making me to stop using the app and now email verification, time to delete",]
df.sort_values(by='score', ascending=True, inplace=True, ignore_index=True)
df = df[(df['score']<=3)]
reviews = []
for review in df['content']:
    print(review)
    reviews.append(review)
request = ' '.join(map(str,reviews))

it = sent_tokenize(request)
# it = summarize("reviews", request)
print("-" * 100)
print(it)