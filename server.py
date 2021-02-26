import os
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from queue import Queue, Empty
import time
import threading
from pipelines import pipeline
import pandas as pd


app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

requests_queue = Queue()
BATCH_SIZE = 10
CHECK_INTERVAL = 0.1

#preload model
nlp = pipeline("multitask-qa-qg")

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
                batch_outputs.append(run(request['input'][0]))

            for request, output in zip(requests_batch, batch_outputs):
                request['output'] = output
		
threading.Thread(target=handle_requests_by_batch).start()


def run(input_text):
    try:
        generated_text = nlp(input_text)
        df = pd.DataFrame(generated_text)
    except ValueError:
        result = 'error'
        return result

    return [df]

# API server
@app.route('/generate', methods=['POST'])
def generate_q():
    if request.method == 'POST':
            
        input_text = str(request.form['input'])

        if len(input_text) == 0:
            return 'No input', 400
        
        if requests_queue.qsize() >= BATCH_SIZE:
            return {'error': 'TooMany requests. please try again'}, 429
        
        req = {
            'input': [input_text]
        }
        requests_queue.put(req)

        while 'output' not in req:
            time.sleep(CHECK_INTERVAL)
            
        if req['output'] == 'error':
            return render_template('index.html', error = 'Invalid text. please try again.'), 400
        
        [df, generated_q] = req['output']
        df = df.to_dict()
        return df
    return None

@app.route('/healthz', methods=['GET'])
def checkHealth():
	return "Alive",200


if __name__ == '__main__':
    app.run(debug=False, port=8080, host='0.0.0.0')
