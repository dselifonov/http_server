FROM python:3.8.1-slim-buster

WORKDIR /usr/src/http_server
COPY . .

EXPOSE 8080
CMD ["python", "httpd.py", "-w", "2", "-r", "/"]