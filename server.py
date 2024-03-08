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


def get_matches(query):
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
        section_matches = [
            elem for elem in data if cleaned_query in elem['section'].lower() or cleaned_query in elem['subsection'].lower()]

        print(f"Title matches: {title_matches}")
        print(f"Abstract matches: {abstract_matches}")
        print(f"Keyword matches: {keyword_article_matches}")
        print(f"Section matches: {section_matches}")

    return title_matches, abstract_matches, keyword_article_matches, section_matches


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
    t_m, a_m, kwa_m, s_m = get_matches(query)

    return render_template('search_results.html', t_matches=t_m, a_matches=a_m, kw_matches=kwa_m, s_mateches=s_m, query=query)


@app.route('/search_link/<query>', methods=['GET'])
def search_results_link(query):
    t_m, a_m, kwa_m, s_m = get_matches(query)

    return render_template('search_results.html', t_matches=t_m, a_matches=a_m, kw_matches=kwa_m, s_mateches=s_m, query=query)


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
    if request.method == 'POST':
        # Extract the form data
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        date = request.form.get('date', '').strip()
        abstract = request.form.get('abstract', '').strip()
        image = request.form.get('image', '').strip()
        image_caption = request.form.get('image_caption', '').strip()

        # Perform validation
        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        if not author:
            errors['author'] = 'Author is required.'
        if not date:
            errors['date'] = 'Date is required.'

        if errors:
            response = jsonify(errors)
            response.status_code = 400
            return response

        # Insert into database (placeholder logic)
        # Replace this with real database interaction
        new_item_id = insert_into_database({
            'title': title,
            'author': author,
            'date': date,
            'abstract': abstract,
            'image': image,
            'image_caption': image_caption
        })

        # Return the ID of the new item
        return jsonify({'id': new_item_id})

    # If it's a GET request, render the 'add_item.html' template
    return render_template('add_item.html')


def insert_into_database(item_data):
    # Placeholder for database insertion logic
    # Assume we return the ID of the new item
    return 123  # Replace with real ID after insertion


if __name__ == '__main__':
    get_nyt_data()
    app.run(debug=True)
