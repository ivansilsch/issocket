

import isocket

client = isocket.Socket()
client.connect('127.0.0.1', 5000)

client.send('hola locos')
