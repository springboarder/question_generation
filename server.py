import os
from flask import Flask, request, send_file, flash, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import io
from queue import Queue, Empty
import time
import threading
from pipelines import pipeline
import pandas as pd





app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

############
############
requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

def handle_requests_by_batch():
    while True:
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE):
            try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue
            batch_outputs = []
            for request in requests_batch:
                batch_outputs.append(run(request['input']))

            for request, output in zip(requests_batch, batch_outputs):
                request['output'] = output
                
threading.Thread(target=handle_requests_by_batch).start()

def run(input_text):
    
    nlp = pipeline("multitask-qa-qg")
    qg = pipeline("e2e-qg")
    
    generated_text = nlp(input_text)
    generated_q = qg(input_text)
    df = pd.DataFrame(generated_text)


    return [df, generated_q]

##############
##############

# Web server
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        input_text = str(request.form['input'])

        if len(input_text) == 0:
            return render_template('index.html', result = 'No Input'), 400

        # nlp = pipeline("multitask-qa-qg")
        # qg = pipeline("e2e-qg")
        # generated_text = nlp(input_text)
        # generated_q = qg(input_text)
        # df = pd.DataFrame(generated_text)

        if requests_queue.qsize() >= BATCH_SIZE:
            return render_template('index.html', result = 'TooMany requests try again'), 429

        req = {
            'input': input_text
        }
        requests_queue.put(req)

        while 'output' not in req:
            time.sleep(CHECK_INTERVAL)
        [df, generated_q] = req['output']

        
        
        return render_template('index.html', result=[df.to_html(classes='data')], titles=df.columns.values, question=generated_q)
            #return redirect(request.url)
    return render_template('index.html')

@app.route('/healthz', methods=['GET'])
def checkHealth():
	return "Pong",200

# @app.errorhandler(413)
# def request_entity_too_large(error):
#     # return {'error': 'File Too Large'}, 413
#     return render_template('index.html', result = 'The image size is too large'), 413

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='0.0.0.0')
