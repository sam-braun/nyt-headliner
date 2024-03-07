# Samuel Braun slb2250

import requests


def format_article_data(article_data):
    formatted_data, all_keywords = [], []
    id = 0

    for article in article_data:
        image_url = ''
        image_caption = ''
        if article['media']:
            first_media_item = article['media'][0]['media-metadata'][2]
            image_url = first_media_item.get('url', '')
            image_caption = article['media'][0].get('caption', '')

        formatted_article = {
            'id': id,
            'url': article['url'],
            "published_date": article['published_date'],
            "update_date": article['updated'],
            'section': article['section'],
            'subsection': article['subsection'],
            'adx_keywords': article['adx_keywords'],
            'byline': article['byline'],
            'title': article['title'],
            'abstract': article['abstract'],
            'image': image_url,
            'image_caption': image_caption,
            'keywords': article['adx_keywords'].split(';')
        }

        formatted_data.append(formatted_article)
        id += 1

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
