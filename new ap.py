import requests
import pandas as pd

url = "https://api.meaningcloud.com/topics-2.0"

df = pd.ExcelFile('app_reviews.xlsx').parse('Fox News - Daily Breaking News')
reviews = []
for review in df['content']:
    reviews.append(review)
    

payload={
    'key': '0251a9cf44bdb55865dfb52ad4994729',
    'txt': ' '.join(map(str,reviews)),
    'lang': 'en',
    'tt': 'concepts'
}

response = requests.post(url, data=payload)

print('Status code:', response.status_code)
print(response.json())