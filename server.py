# Samuel Braun slb2250

from flask import Flask, redirect, url_for
from flask import render_template
from flask import Response, request, jsonify
import nyt_helper as nyt

app = Flask(__name__)

global_id = 100


def get_nyt_data():
    api_key = "AjqDOaTFAm1qxTherm3JbH3djF3cIUlg"
    request_url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json?api-key={api_key}"
    global data, all_keywords
    data, all_keywords = nyt.get_nyt_data(request_url)

    global id
    id = 0
    for article in data:
        article['id'] = id
        id += 1


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
    global global_id  # Declare global_id to modify it

    if request.method == 'POST':
        # Extract the form data
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        update_date = request.form.get('update_date', '').strip()
        url = request.form.get('url', '').strip()
        section = request.form.get('section', '').strip()
        subsection = request.form.get('subsection', '').strip()
        abstract = request.form.get('abstract', '').strip()
        image = request.form.get('image', '').strip()

        # Perform validation
        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        if not author:
            errors['author'] = 'Author is required.'
        if not update_date:
            errors['update_date'] = 'Date is required.'
        if not url:
            errors['url'] = 'URL is required.'

        if errors:
            response = jsonify(errors)
            response.status_code = 400
            return response

        # Simulate database insertion by adding the new article to the 'data' list
        new_article = {
            'id': global_id,
            'title': title,
            'author': author,
            'update_date': update_date,
            'section': section,
            'subsection': subsection,
            'url': url,
            'abstract': abstract,
            'image': image
        }

        data.append(new_article)
        global_id += 1  # Increment the ID for the next article

        return jsonify(new_article)

    # If it's a GET request, render the 'add_item.html' template
    return render_template('add_item.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    global data  # Make sure we're modifying the global data variable
    article = next((article for article in data if article['id'] == id), None)

    if not article:
        return "Item not found", 404

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        date = request.form['date']
        url = request.form['url']
        section = request.form['section']
        subsection = request.form['subsection']
        abstract = request.form.get('abstract', '')
        image = request.form.get('image', '')

        if not (title and author and date):
            return jsonify({'error': 'Required fields are missing'}), 400

        # Update the article directly in the data list
        for i, art in enumerate(data):
            if art['id'] == id:
                data[i]['title'] = title
                data[i]['author'] = author
                data[i]['published_date'] = date
                data[i]['url'] = url
                data[i]['section'] = section
                data[i]['subsection'] = subsection
                data[i]['abstract'] = abstract
                data[i]['image'] = image
                break  # Stop iterating once we've found and updated the article

        # Redirect to the view page after updating
        return redirect(url_for('item', id=id))

    # If it's a GET request, render the edit page with the article data
    return render_template('edit_item.html', article=article)


if __name__ == '__main__':
    get_nyt_data()
    app.run(debug=True)
