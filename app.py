from flask import Flask, render_template, request
from threading import Thread
from googlesearch import search
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from flask_sslify import SSLify
import os
import time
import uuid

load_dotenv()

uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client['user_data']
collection = db['searches']

app = Flask(__name__)
sslify = SSLify(app)
results = {}

def background_search(query, id, ip_address):
    print(f"Starting search for query: {query}")
    print(f"IP Address: {ip_address}")
    start_time = time.monotonic()
    urls = []
    for url in search(query):
        urls.append(url)
        time.sleep(2)
    print(f"Search completed. Found {len(urls)} results.")
    for item in urls:
        index = urls.index(item)
        print(f"Link {index}: {item}")
    end_time = time.monotonic()
    execution_time = round(end_time - start_time, 2)
    results[id] = (urls, execution_time)
    collection.insert_one({'ip': ip_address, 'query': query, 'num_results': len(urls), 'uuid': id, 'execution_time': execution_time, 'timestamp': datetime.now(), 'urls': urls})

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        user_ip = request.remote_addr
    if request.method == 'POST':
        query = request.form.get('query')
        id = str(uuid.uuid4())
        Thread(target=background_search, args=(query, id, user_ip)).start()
        return render_template('loading.html', id=id, user_ip=user_ip)
    return render_template('index.html')

@app.route('/results/<id>')
def results_page(id):
    if id in results:
        urls, execution_time = results[id]
        return render_template('results.html', urls=urls, execution_time=execution_time, num_results=len(urls))
    return "Results not ready, please refresh the page."


# Driver's Code
if __name__ == '__main__':
    app.run(debug=True)