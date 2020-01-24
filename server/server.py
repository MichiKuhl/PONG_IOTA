import socket 
import select 
import sys 
from thread import *
from iota.crypto.addresses import AddressGenerator

file  = open("pong.conf","r")
pong_conf=file.readlines()
file.close()
address_num = int(pong_conf[0])
seed = "SEED9SEED9SEED9"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  
IP_address = "0.0.0.0"
  
Port = 5555 
server.bind((IP_address, Port)) 
  
server.listen(200) 
  
list_of_clients = []  

print "Server initialization done"
  
def clientthread(conn, addr): 
    global address_num  
    global seed
    conn.send("Connected to the PONG Server") 
    client_num = address_num
    address_num = address_num + 1
    file = open("pong.conf","w")
    file.write(str(address_num))
    file.close()
    generator = AddressGenerator(seed,1,True)
    addresses = generator.get_addresses(client_num, count=1)[0]
    conn.send(str(addresses))


    while True: 
            try: 
                message = conn.recv(2048) 
                if message: 
  
                    print "<" + addr[0] + "> " + message 
                    broadcast(message, conn) 
  
                else: 
                    remove(conn) 
  
            except KeyboardInterrupt:
                    server.close()
            except: 
                    continue

  
def broadcast(message, connection): 
    for i in range(len(list_of_clients)): 
                if list_of_clients[i][0] != connection:
                        if message.split(' ')[0] in list_of_clients[i][1]: 
                                try: 
                                        clients = list_of_clients[i][0]
                                        clients.send(message.split(' ')[1]) 
                                except KeyboardInterrupt:
                                        clients.close()
                                        server.close()
                                except: 
                                        clients.close()   
                                        remove(clients) 

def remove(connection): 
    if connection in list_of_clients: 
        list_of_clients.remove(connection) 
  
def main():
        try: 
            while True:
                conn, addr = server.accept() 
                list_of_clients.append([conn,addr[0]])
                print addr[0] + " connected"
                start_new_thread(clientthread,(conn,addr))     
        except KeyboardInterrupt:
                conn.close() 
                server.close() 
        except:
                main()
main()

