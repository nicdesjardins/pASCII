from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from constants import Commands, Constants

Constants = Constants()
#import struct

from packet import pASCII_packet as Packet

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

packet = Packet()

charsInSpace = {}

def accept_incoming_connection():
    while True:
        client, client_address = server.accept()
        print("Client "+str(client.fileno())+" (%s:%s) has connected." % client_address)
        
            
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def sendCharsInSpaceToClient(client):
    for (y, x) in charsInSpace:
        packet = Packet()
        packet.y = y
        packet.x = x
        packet.ch = charsInSpace[(y, x)]
        client.sendall(packet.pack())
        
def handle_client(client):
    sock = client.recv(packet.size)
    clients[client] = 'a'
    
    while True:
        try:
            data = client.recv(packet.size)
            packet.unpack(data)
            print("From "+str(client.fileno())+" got "+str(packet))
            if isClientQuit(packet):
                print('client '+str(client.fileno())+' left')
                client.sendall(data)
                client.close()
                del clients[client]
            elif isCharInSpaceRequest(packet):
                sendCharsInSpaceToClient(client)
            else:
                charsInSpace[(packet.y, packet.x)] = packet.ch
                broadcast(data, client)
        except:
            pass
def isCharInSpaceRequest(packet):
    return packet.msg == Constants.Commands.CHARSINSPACE

def isClientQuit(packet):
    return packet.msg == Constants.Commands.QUIT
        
def broadcast(data, client):
    for sock in clients:
        if sock.fileno() != client.fileno():
            sock.sendall(data)

if __name__ == '__main__':
    server.listen(5) # listen for 5 connections max
    print('Waiting for connections on %s:%s' % (HOST, PORT))
    ACCEPT_THREAD = Thread(target=accept_incoming_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    server.close()
