import random
from flask import Flask, redirect, url_for
from flask import render_template
from flask import Response, request, jsonify
import nyt_helper as nyt
import re
from markupsafe import escape


app = Flask(__name__)

global_id = 100


def get_nyt_data():
    api_key = "your_api_key"
    request_url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json?api-key={api_key}"
    global data, all_keywords
    data, all_keywords = nyt.get_nyt_data(request_url)

    global id
    id = 0
    for article in data:
        article['id'] = id
        id += 1


def get_matches(query):
    if not query:
        return [], [], [], 0

    cleaned_query = query.lower().strip()
    title_matches = [
        elem for elem in data if cleaned_query in elem['title'].lower()]
    abstract_matches = [
        elem for elem in data if cleaned_query in elem['abstract'].lower()]
    keyword_matches = [
        kw for kw in all_keywords if cleaned_query in kw.lower()]
    keyword_article_matches = [elem for elem in data if any(
        kw in elem['keywords'] for kw in keyword_matches)]

    unique_articles = {}
    for article in title_matches + abstract_matches + keyword_article_matches:
        if article['id'] not in unique_articles:
            unique_articles[article['id']] = article

    all_articles = list(unique_articles.values())
    article_count = len(all_articles)

    return title_matches, abstract_matches, all_articles, article_count


def highlight_term(original_text, term):
    """Highlight the term in the text, case-insensitively, without modifying the original text."""
    escaped_term = escape(term)
    escaped_text = escape(original_text)
    highlighted_text = re.sub(r'(?i)(' + re.escape(escaped_term) + r')',
                              r'<strong>\1</strong>', escaped_text, flags=re.IGNORECASE)
    return highlighted_text


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/api/featured_items')
def featured_items():
    article_count = len(data)

    indices = random.sample(range(article_count), 6)
    featured = [data[i] for i in indices]

    return jsonify(featured)


@app.route('/search', methods=['GET'])
def search_results():
    query = request.args.get('query', '')
    t_m, a_m, kwa_m, article_count = get_matches(query)

    for matches in (t_m, a_m, kwa_m):
        for match in matches:
            match['display_title'] = highlight_term(match['title'], query)

    no_matches_found = article_count == 0

    return render_template('search_results.html', t_matches=t_m, a_matches=a_m, kw_matches=kwa_m, query=query, total_matches=article_count, no_matches_found=no_matches_found)


@app.route('/search_link/<query>', methods=['GET'])
def search_results_link(query):
    t_m, a_m, kwa_m, article_count = get_matches(query)

    for matches in (t_m, a_m, kwa_m):
        for match in matches:
            match['display_title'] = highlight_term(match['title'], query)

    no_matches_found = article_count == 0

    return render_template('search_results.html', t_matches=t_m, a_matches=a_m, kw_matches=kwa_m, query=query, total_matches=article_count, no_matches_found=no_matches_found)


@app.route('/view/<id>')
def item(id):
    try:
        item_id = int(id)
    except ValueError:
        return "Invalid Item ID", 400

    item = next((item for item in data if item['id'] == item_id), None)
    if item:
        print(item)
        return render_template('view_item.html', item=item)
    else:
        return "Item not found", 404


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    global global_id

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        date = request.form.get('date', '').strip()
        url = request.form.get('url', '').strip()
        section = request.form.get('section', '').strip()
        subsection = request.form.get('subsection', '').strip()
        abstract = request.form.get('abstract', '').strip()
        image = request.form.get('image', '').strip()

        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        if not author:
            errors['author'] = 'Author is required.'
        if not date:
            errors['date'] = 'Date is required.'
        if not url:
            errors['url'] = 'URL is required.'

        if errors:
            response = jsonify(errors)
            response.status_code = 400
            return response

        new_article = {
            'id': global_id,
            'title': title,
            'author': author,
            'published_date': date,
            'update_date': date,
            'section': section,
            'subsection': subsection,
            'url': url,
            'abstract': abstract,
            'image': image
        }

        data.append(new_article)
        global_id += 1

        return jsonify(new_article)

    return render_template('add_item.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    global data
    article = next((article for article in data if article['id'] == id), None)

    if not article:
        return "Item not found", 404

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        update_date = request.form['update_date']
        url = request.form['url']
        section = request.form['section']
        subsection = request.form['subsection']
        abstract = request.form.get('abstract', '')
        image = request.form.get('image', '')

        if not (title and author and update_date):
            return jsonify({'error': 'Required fields are missing'}), 400

        for i, art in enumerate(data):
            if art['id'] == id:

                data[i]['title'] = title
                data[i]['author'] = author
                data[i]['update_date'] = update_date
                data[i]['url'] = url
                data[i]['section'] = section
                data[i]['subsection'] = subsection
                data[i]['abstract'] = abstract
                data[i]['image'] = image
                break

        return redirect(url_for('item', id=id))

    return render_template('edit_item.html', article=article)


if __name__ == '__main__':
    get_nyt_data()
    app.run(debug=True)
