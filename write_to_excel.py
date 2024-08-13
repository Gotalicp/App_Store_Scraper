import pandas as pd
import json
import os
import re

def sanitize_sheet_name(name):
    sanitized_name = re.sub(r'[\\/*?:[]|]', '', name)
    return sanitized_name[:31]

def save_reviews_to_excel(apps, filename='app_store_apps.xlsx'):
    try:
        if os.path.exists(filename):
            sheet_names = pd.ExcelFile(filename).sheet_names
            if 'Apps' in sheet_names:
                existing_data = pd.read_excel(filename, sheet_name='Apps')
            else:
                existing_data = pd.DataFrame()
        else:
            existing_data = pd.DataFrame()

        apps_data = pd.DataFrame(apps)
        apps_data_no_reviews = apps_data.drop(columns=['Reviews'])
        combined_data = pd.concat([existing_data, apps_data_no_reviews], ignore_index=True)
        combined_data = combined_data.drop_duplicates(subset=['id'], keep='last')

        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            combined_data.to_excel(writer, sheet_name='Apps', index=False, startrow=1, header=False)

            workbook = writer.book
            worksheet = writer.sheets['Apps']

            header_format = workbook.add_format({'bold': True})
            for col_num, value in enumerate(combined_data.columns.values):
                worksheet.write(0, col_num, value, header_format)

            for row_num, app in enumerate(combined_data.itertuples(), start=1):
                worksheet.write_url(row_num, 0, app.link, string=app.Name)
                worksheet.write_url(row_num, 8, app.devLink, string=app.Developer)

            for app in apps_data.itertuples():
                reviews = app.Reviews
                if reviews:
                    try:
                        if isinstance(reviews, list) and len(reviews) > 0 and isinstance(reviews[0], dict):
                            reviews_df = pd.DataFrame(reviews)
                        elif isinstance(reviews, list) and len(reviews) > 0 and isinstance(reviews[0], list):
                            reviews_df = pd.DataFrame(reviews)
                        else:
                            reviews_df = pd.DataFrame()
                    except Exception as e:
                        print(f"Error converting reviews to DataFrame: {e}")
                        reviews_df = pd.DataFrame()

                    sheet_name = sanitize_sheet_name(f'{app.OS}-{app.Name}')
                    reviews_df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        print(f"Failed to write Excel file: {e}")

def json_to_apps(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except UnicodeDecodeError as e:
        print(f"Error reading the JSON file: {e}")
        return []

    app_info_list = []

    for id in data:
        app_info = data.get(id)
        app_info_list.append(
            {
            'Name': app_info.get('Name'),
            'OS': app_info.get('OS', 'N/A'),
            'Tag': app_info.get('Tag', 'N/A'),
            'Rating': app_info.get('Rating', 'N/A'),
            'Downloads': app_info.get('Downloads', 'N/A'),
            'Review_Count': app_info.get('Review_Count', 'N/A'),
            'Reviews': app_info.get('Reviews', []),
            'Country': app_info.get('Country', 'N/A'),
            'Release_date': app_info.get('Release_date', 'N/A'),
            'Developer': app_info.get('Developer', 'N/A'),
            'link': app_info.get('link', 'N/A'),
            'devLink': app_info.get('devLink', 'N/A'),
            'id': app_info.get('id', 'N/A')
        }
        )
    return app_info_list

def main():
    json_file = 'apps.json'
    excel_file = 'apps.xlsx'

    apps = json_to_apps(json_file)
    save_reviews_to_excel(apps, filename=excel_file)

if __name__ == '__main__':
    main()