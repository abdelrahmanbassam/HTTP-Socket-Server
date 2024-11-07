import socket
import threading
import sys


#we can change the protocol to any other string
DISCONNECT_PORTOCOL = "DISCONNECT!"

def connectClient(connection,address):
    print(f"[New Connection] from {address} has been established!")
    isConneted = True
    while isConneted:
        # Receive the data with a size of 1024 bytes(we can increase/decrease the size)
        massegeLength = connection.recv(1024).decode()
        if not massegeLength:
            break

        massegeLength = int(massegeLength)
        request = connection.recv(massegeLength).decode()

        if request == DISCONNECT_PORTOCOL:
            isConneted = False

        # Parse request type (GET or POST)
        requestHeader = request.splitlines()
        command, filePath = requestHeader[0].split()

        if command == "GET":
            print(f"[GET REQUEST] {filePath}")
            getRequestHandler(connection, filePath)

        elif command == "POST":
            print(f"[POST REQUEST] {filePath}")
            postRequestHandler(connection, filePath, request)

        else:
            connection.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
    connection.close()
    print(f"[CONNECTION CLOSED] {address}")

def getRequestHandler(connection, filePath):
    pass

def postRequestHandler(connection, filePath, request):
    pass

def startServer(port):
    # Server Configuration
    LOCAL_IP = socket.gethostbyname(socket.gethostname())# Get the IP address of the server 
    ADDRESS = (LOCAL_IP, port) 

    # Create a socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDRESS)
    server.listen()
    print(f"[LISTENING] Server is listening on {LOCAL_IP} on PORT:{port}")

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    startServer(port)