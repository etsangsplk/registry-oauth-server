FROM python:2.7-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /server
ADD requirements.txt /server/requirements.txt
WORKDIR /server
RUN pip install -r requirements.txt

ADD . /server
EXPOSE 8080
CMD python app.py
