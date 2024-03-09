# Samuel Braun slb2250

import requests
import datetime


def process_keywords(keyword_string):
    if keyword_string:
        keywords = keyword_string.split(';')
        for kw in keywords:
            if ', ' in kw:
                keywords.remove(kw)
                name = kw.split(', ')
                correct_name = f"{name[1]} {name[0]}"
                keywords.append(correct_name)

        return keywords


def format_article_data(article_data):
    formatted_data, all_keywords = [], []

    for article in article_data:
        image_url, image_caption = '', ''

        if article['media']:
            first_media_item = article['media'][0]['media-metadata'][2]
            image_url = first_media_item.get('url', '')
            image_caption = article['media'][0].get('caption', '')

        # published_date = datetime.strptime(article['published_date'], "%Y-%m-%d").strftime("%B %d, %Y")

        keywords = process_keywords(article['adx_keywords'])
        article['byline'] = article['byline'].replace('By ', '')
        article['updated'] = article['updated'][:-9]

        formatted_article = {
            'url': article['url'],
            "published_date": article['published_date'],
            "update_date": article['updated'],
            'section': article['section'],
            'subsection': article['subsection'],
            'adx_keywords': article['adx_keywords'],
            'author': article['byline'],
            'title': article['title'],
            'abstract': article['abstract'],
            'image': image_url,
            'image_caption': image_caption,
            'keywords': keywords
        }

        if formatted_article["image"]:
            formatted_data.append(formatted_article)

        for keyword in formatted_article['keywords']:
            if keyword not in all_keywords:
                all_keywords.append(keyword)

    print("Article data correctly formatted.")
    return formatted_data, all_keywords


def get_nyt_data(request_url):
    requestHeaders = {
        "Accept": "application/json"
    }

    response = requests.get(request_url, headers=requestHeaders)
    article_data = response.json()["results"]
    print("Data successfully retrieved from NYT API.")

    return format_article_data(article_data)
