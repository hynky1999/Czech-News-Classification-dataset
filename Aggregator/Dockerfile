FROM python:3.10
WORKDIR /var/lib/Aggregator
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./App ./App
ENTRYPOINT [ "python3", "-m", "App.stomp_aggregate"]



 
