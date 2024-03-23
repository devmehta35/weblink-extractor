from flask import Flask, render_template, request
from threading import Thread
import time
from googlesearch import search

app = Flask(__name__)
results = {}

def background_search(query, id):
    # print(f"Starting search for query: {query}")
    start_time = time.monotonic()
    urls = [url for url in search(query)]
    # print(f"Search completed. Found {len(urls)} results.")
    end_time = time.monotonic()
    execution_time = end_time - start_time
    results[id] = (urls, execution_time)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form.get('query')
        id = str(time.time())  # Use the current time as a unique id
        Thread(target=background_search, args=(query, id)).start()
        return render_template('loading.html', id=id)
    return render_template('index.html')

@app.route('/results/<id>')
def results_page(id):
    if id in results:
        urls, execution_time = results[id]
        return render_template('results.html', urls=urls, execution_time=execution_time, num_results=len(urls))
    return "Results not ready, please refresh the page."


if __name__ == '__main__':
    app.run(debug=True)
