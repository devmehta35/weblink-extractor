from flask import Flask, render_template, request
from threading import Thread
import time
import uuid
from googlesearch import search

app = Flask(__name__)
results = {}

def background_search(query, id, ip_address):
    print(f"Starting search for query: {query}")
    print(f"IP Address: {ip_address}" )
    start_time = time.monotonic()
    urls = []
    for url in search(query):
        urls.append(url)
        time.sleep(1)  # Add a delay of 1 second between requests
    for item in urls:
        index = urls.index(item)
        print(f"Link {index} => {item}")
    print(f"Search completed. Found {len(urls)} results.")
    end_time = time.monotonic()
    execution_time = round(end_time - start_time, 2)  # Round off to 2 decimal places
    results[id] = (urls, execution_time)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form.get('query')
        id = str(uuid.uuid4())
        ip_address = request.remote_addr
        Thread(target=background_search, args=(query, id, ip_address)).start()
        return render_template('loading.html', id=id)
    return render_template('index.html')

@app.route('/results/<id>')
def results_page(id):
    if id in results:
        urls, execution_time = results[id]
        return render_template('results.html', urls=urls, execution_time=execution_time, num_results=len(urls))
    return "Results not ready, please refresh the page."

# Driver's Code
# if __name__ == '__main__':
#     app.run(debug=True)