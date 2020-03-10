Web server test suite
=====================

Implement a Web server. Libraries for helping manage TCP socket connections *may* be used (if server is asynchronous [epoll](https://github.com/m13253/python-asyncore-epoll) *must* be used). Libraries that implement any part of HTTP or multiprocessing model *must not* be used.

## Requirements ##

* Respond to `GET` with status code in `{200,403,404}`
* Respond to `HEAD` with status code in `{200,404}`
* Respond to all other request methods with status code `405`
* Directory index file name `index.html`
* Respond to requests for `/<file>.html` with the contents of `DOCUMENT_ROOT/<file>.html`
* Requests for `/<directory>/` should be interpreted as requests for `DOCUMENT_ROOT/<directory>/index.html`
* Respond with the following header fields for all requests:
  * `Server`
  * `Date`
  * `Connection`
* Respond with the following additional header fields for all `200` responses to `GET` and `HEAD` requests:
  * `Content-Length`
  * `Content-Type`
* Respond with correct `Content-Type` for `.html, .css, js, jpg, .jpeg, .png, .gif, .swf`
* Respond to percent-encoding URLs
* No security vulnerabilities!
* **Bonus:** init script for daemonization with commands: start, stop, restart, status

## Testing ##

* `httptest` folder from `http-test-suite` repository should be copied into `DOCUMENT_ROOT`
* Your HTTP server should listen `localhost:80`
* `http://localhost/httptest/wikipedia_russia.html` must been shown correctly in browser
* Lowest-latency response (tested using `ab`, ApacheBench) in the following fashion: `ab -n 50000 -c 100 -r http://localhost:8080/`

## Architecture ##
Linux select.epoll with multiprocessing have been chosen for task. 


## AB Test Results ##
```shell script
Server Software:        DS
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        9 bytes

Concurrency Level:      100
Time taken for tests:   4.325 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      7000000 bytes
HTML transferred:       450000 bytes
Requests per second:    11559.72 [#/sec] (mean)
Time per request:       8.651 [ms] (mean)
Time per request:       0.087 [ms] (mean, across all concurrent requests)
Transfer rate:          1580.43 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    3  50.6      0    1031
Processing:     0    5  10.7      4     412
Waiting:        0    5  10.6      4     411
Total:          0    8  57.5      5    1440

Percentage of the requests served within a certain time (ms)
  50%      5
  66%      5
  75%      6
  80%      6
  90%      7
  95%      9
  98%     11
  99%     14
 100%   1440 (longest request)
```