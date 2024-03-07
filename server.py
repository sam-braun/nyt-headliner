# Samuel Braun slb2250

from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
import nyt_helper as nyt

app = Flask(__name__)


def get_nyt_data():
    api_key = "AjqDOaTFAm1qxTherm3JbH3djF3cIUlg"
    request_url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json?api-key={api_key}"
    global data, all_keywords
    data, all_keywords = nyt.get_nyt_data(request_url)


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/api/featured_items')
def featured_items():
    featured = data[:3]
    return jsonify(featured)


@app.route('/search', methods=['GET'])
def search_results():
    query = request.args.get('query', '')
    # matches = []
    if query:
        cleaned_query = query.lower().strip()
        title_matches = [
            elem for elem in data if cleaned_query in elem['title'].lower()]
        abstract_matches = [
            elem for elem in data if cleaned_query in elem['abstract'].lower()]
        keyword_matches = [
            kw for kw in all_keywords if cleaned_query in kw.lower()]
        keyword_article_matches = [
            elem for elem in data if any(
                kw in elem['keywords'] for kw in keyword_matches)]

        print(f"Title matches: {title_matches}")
        print(f"Abstract matches: {abstract_matches}")
        print(f"Keyword matches: {keyword_article_matches}")

    return render_template('search_results.html', t_matches=title_matches, a_matches=abstract_matches, kw_matches=keyword_article_matches, query=query)


@app.route('/view/<id>')
def item(id):
    item = next((item for item in data if item['id'] == id), None)
    if item:
        return render_template('view_item.html', item=item)
    else:
        return "Item not found", 404


if __name__ == '__main__':
    get_nyt_data()
    app.run(debug=True)
