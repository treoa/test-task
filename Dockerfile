FROM python:3.7.9-slim
COPY . .

RUN pip3 install -r requirements.txt
