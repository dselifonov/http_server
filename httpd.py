import argparse
import os

from src.http.server import HTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("host", type=str)
    # parser.add_argument("port", type=int)
    # parser.add_argument("name", type=str)
    parser.add_argument("-w", type=int, default=4, help="Number of workers")
    parser.add_argument("-r", type=str, default='httptest', help="Documents root")
    args = parser.parse_args()

    server = HTTPServer('0.0.0.0', 8080, 'localhost', os.path.join(BASE_DIR, args.r.lstrip('/')), args.w)
    try:
        print('Starting server, use <Ctrl-C> to stop')
        server.run()
    except KeyboardInterrupt:
        print('Server has been stopped')
