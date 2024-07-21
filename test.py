from google_play_scraper import app, search, reviews , Sort
import pandas as pd
from datetime import datetime, timedelta
import re

def get_google_play_apps(category):
    try:
        results = search(
            category,
            lang='en',
            country='us',
            n_hits=40
        )
    except Exception as e:
        print(f"Failed to search for apps: {e}")
        return []

    app_details = []
    for result in results:
        if result['score'] < 4.0:
            try:
                app_info = app(result['appId'])
                app_details.append({
                    'name': app_info['title'],
                    'developer': app_info['developer'],
                    'rating': app_info['score'],
                    'reviews': app_info['ratings'],
                    'installs': app_info['realInstalls'],
                    'link': f"https://play.google.com/store/apps/details?id={app_info['appId']}",
                    'appId': app_info['appId']
                })
            except Exception as e:
                print(f"Failed to retrieve app details for {result['appId']}: {e}")
                continue
        
    return app_details

def get_reviews(app_id):
    review_list = []
    all_reviews_fetched = False
    page = 0
    max_pages = 10
    continuation_token = None    
    while not all_reviews_fetched and page < max_pages:
        try:
            new_reviews, continuation_token  = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                continuation_token = continuation_token
            )
        except Exception as e:
            print(f"Failed to retrieve reviews for {app_id} on page {page}: {e}")
            break
        
        if not new_reviews:
            all_reviews_fetched = True
        else:
            review_list.extend(new_reviews)
            page += 1
            
    return review_list

def filter_reviews_by_date(review_list, months_ago):
    cutoff_date = datetime.now() - timedelta(days=months_ago * 30)
    
    filtered_reviews = []
    
    for review in review_list:
        review_date = review['at']
        if review_date >= cutoff_date:
            review['at'] = review_date.strftime('%Y-%m-%d %H:%M:%S')
            filtered_reviews.append(review)
    
    return filtered_reviews

def sanitize_sheet_name(sheet_name):
    sanitized_name = re.sub(r'[\\/*?[\]:]', '', sheet_name)
    return sanitized_name[:30]

def save_reviews_to_excel(apps, filename='app_reviews.xlsx'):
    try:
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            for app in apps:
                review_list = get_reviews(app['appId'])
                filtered_reviews = filter_reviews_by_date(review_list, 6)
                
                if filtered_reviews:
                    reviews_df = pd.DataFrame(filtered_reviews)
                    sheet_name = sanitize_sheet_name(app['name'])
                    reviews_df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        print(f"Failed to write Excel file: {e}")

if __name__ == "__main__":
    category = "NEWS"
    apps = get_google_play_apps(category)
    for app in apps:
        print(f"Name: {app['name']}")
        print(f"Developer: {app['developer']}")
        print(f"Rating: {app['rating']}")
        print(f"Reviews: {app['reviews']}")
        print(f"Downloads: {app['installs']}")
        print(f"Link: {app['link']}")
        print("-" * 40)
    
    save_reviews_to_excel(apps)