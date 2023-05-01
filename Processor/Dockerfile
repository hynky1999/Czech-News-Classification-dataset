FROM python:3.10
WORKDIR /var/lib/Processor
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./App ./App
COPY ./CZExtractors ./CZExtractors
COPY ./config.json .
ENTRYPOINT [ "python3", "-m", "App.stomp_process", "config.json"]