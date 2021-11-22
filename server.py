from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
#import struct

from packet import pASCII_packet

clients = {}
addresses = {}

HOST = ''

PORT = input('Port [default: 1234]: ')
if not PORT:
    PORT = 1234
else:
    PORT = int(PORT)

ADDR = (HOST, PORT)

server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDR)

packet = pASCII_packet()

def accept_incoming_connection():
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
    sock = client.recv(packet.size)
    clients[client] = 'a'
    
    while True:
        try:
            data = client.recv(packet.size)
            
            if isClientQuit(data):
                print('client '+str(client.fileno())+' leaving')
                client.sendall(data)
                client.close()
                del clients[client]
            else:
                broadcast(data, client)
        except:
            pass
    
def isClientQuit(data):
    y, x, ch, msg, detail = packer.unpack(data)
    return msg == 'QUIT'
        
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
