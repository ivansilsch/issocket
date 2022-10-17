

import isocket

try:

    server = isocket.Socket()
    server.bind('127.0.0.1', 5000)
    server.listen()

    try:
        while True:
            print(server.recv())

    except Exception as e:
        server.close()
        print(e)

except KeyboardInterrupt as e:
    server.close()
    print(e)
