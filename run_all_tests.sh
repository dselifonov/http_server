docker build -t http_server .
docker run -p 8080:8080 -d --name http_server http_server
docker exec http_server python httptest.py
docker exec http_server ab -n 50000 -c 100 -r http://localhost:8080/