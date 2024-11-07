import socket
import threading

#we can change the protocol to any other string
DISCONNECT_PORTOCOL = "DISCONNECT!"

def connectClient(connection,address):
    print(f"[New Connection] from {address} has been established!")
    isConneted = True
    while isConneted:
        # Receive the data with a size of 1024 bytes(we can increase/decrease the size)
        massegeLength = connection.recv(1024).decode()
        if massegeLength:
            massegeLength = int(massegeLength)
            data = connection.recv(massegeLength).decode()
            if data == DISCONNECT_PORTOCOL:
                isConneted = False
            print(f"[{address}] {data}")
        else:
            isConneted = False
    connection.close()

def startServer():
    # Server Configuration
    PORT = 8080
    LOCAL_IP = socket.gethostbyname(socket.gethostname())# Get the IP address of the server 
    ADDRESS = (LOCAL_IP, PORT) 

    # Create a socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDRESS)
    server.listen()
    print(f"[LISTENING] Server is listening on {LOCAL_IP} on PORT:{PORT}")

    # Accept the connection from the client and create a thread to handle the connection
    while True:
        #this will block the code until a connection is made
        connection, address = server.accept()
        
        # Create a thread to handle the connection take the connection and the address as arguments
        thread = threading.Thread(target=connectClient, args=(connection,address))
        thread.start()
        print("[NEW CONNECTION FROM A CLIENT]")
        #Subtract the main thread from the active threads
        print(f"[NUMBER OF CONNECTIONS] {threading.activeCount() - 1}")

startServer()