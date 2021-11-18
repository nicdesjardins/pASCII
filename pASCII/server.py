from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import struct

clients = {}
addresses = {}

HOST = ''
PORT = 1234
ADDR = (HOST, PORT)

server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDR)

packer = struct.Struct('I I I')

def accept_incoming_connection():
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
    sock = client.recv(packer.size)
    clients[client] = 'a'
    
    while True:

        data = client.recv(packer.size)
        broadcast(data, client)

def broadcast(data, client):
    print('IN FROM '+ str(client.fileno()) + ': ' + str(packer.unpack(data)))
    for sock in clients:
        if sock.fileno() != client.fileno():
            print('\t- SENT TO ' + str(sock.fileno())+'')
            sock.sendall(data)

if __name__ == '__main__':
    server.listen(5) # listen for 5 connections max
    print('Waiting for connections on %s:%s' % (HOST, PORT))
    ACCEPT_THREAD = Thread(target=accept_incoming_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    server.close()
