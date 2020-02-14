import asyncio
import sys

counter = 0


async def read_request(reader, delimiter=b'!'):
    request = bytearray()
    try:
        while True:
            chunk = await reader.read(4)
            if not chunk:
                return None
            request += chunk
            if delimiter in request:
                return request
    except ConnectionResetError:
        return None


async def handle_request(request):
    await asyncio.sleep(5)
    return request[::-1]


async def write_response(writer, response, cid):
    writer.write(response)
    await writer.drain()
    writer.close()
    print(f"Client #{cid} has been served.")


async def serve_client(reader, writer):
    global counter
    cid = counter
    counter += 1

    print(f"Client #{cid} connected.")

    request = await read_request(reader)
    if request is None:
        print(f"Client #{cid} disconnected.")
        return
    response = await handle_request(request)
    await write_response(writer, response, cid)


async def run_server(host, port):
    server = await asyncio.start_server(serve_client, host, port)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run_server('127.0.0.1', int(sys.argv[1])))
