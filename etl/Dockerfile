FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt
COPY es_mapping.json es_mapping.json

RUN pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY src .

ENTRYPOINT ["python", "__main__.py"]