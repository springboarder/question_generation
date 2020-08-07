FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-devel

COPY . .
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt

EXPOSE 8080

RUN python3 pre_load.py
COPY . .

CMD python3 server.py
