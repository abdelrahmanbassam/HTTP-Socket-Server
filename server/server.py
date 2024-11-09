import socket
import threading
import sys
import os

CHUNK_SIZE = 1024
DEFAULT_TIMEOUT = 10

def connectClient(connection, address):
    print(f"[New Connection] from {address} has been established!")
    isConnected = True
    
    while isConnected:
        try:
            # Dynamically adjust the timeout
            active_connections = threading.active_count() - 1
            timeout = max(DEFAULT_TIMEOUT / (active_connections + 1), 1)
            connection.settimeout(timeout)
            
            request = b""
            while True:
                chunk = connection.recv(CHUNK_SIZE)
                if not chunk:
                    break
                request += chunk
                if b"\r\n\r\n" in request:
                    break
            if not request:
                break
            try:
                requestHeader = request.split(b"\r\n\r\n")[0].decode()
            except UnicodeDecodeError:
                connection.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                break
            # Parse request type (GET or POST)
            requestLines = requestHeader.split("\r\n")
            content_length = requestHeader.split("Content-Length: ")[1].split("\r\n")[0] if "Content-Length: " in requestHeader else 0
            command = requestLines[0].split()[0]
            filePath = requestLines[0].split()[1].lstrip('/')
            data = request.split(b"\r\n\r\n")[1] if b"\r\n\r\n" in request else b""
            while len(data) < int(content_length):
                data += connection.recv(CHUNK_SIZE)
            
            if command == "GET":
                print(f"[GET REQUEST] {filePath}")
                getRequestHandler(connection, filePath)
            elif command == "POST":
                print(f"[POST REQUEST] {filePath}")
                postRequestHandler(connection, filePath, data)
            else:
                connection.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                
            if "Connection: close" in requestHeader:
                isConnected = False
            
        except socket.timeout:
            print(f"[TIMEOUT] {address} has been disconnected!")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            break
    connection.close()
    print(f"[CONNECTION CLOSED] {address}")

def getRequestHandler(connection, filePath): 
    filePath = filePath.lstrip("/")
    if os.path.exists(filePath):
        with open(filePath, 'rb') as file:
            data = file.read()
        response = b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(data)).encode() + b"\r\n\r\n" + data
    else:
        # If the file does not exist, return a 404 response to the browser
        response = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
        response += b"<html><body><h1>404 Not Found</h1></body></html>"
    connection.send(response)

def postRequestHandler(connection, filePath, data):
    filePath = filePath.lstrip("/")
    with open(filePath, 'wb') as file:
        file.write(data)
    response = b"HTTP/1.1 201 Created\r\nContent-Type: text/html\r\n\r\n"
    response += b"<html><body><h1>File Created</h1></body></html>"
    connection.send(response)

def startServer(port=8080):
    # Server Configuration
    # Get the IP address of the server
    LOCAL_IP = socket.gethostbyname(socket.gethostname())
    ADDRESS = (LOCAL_IP, port)

    # Create a socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # SOCK_STREAM for TCP
    server.bind(ADDRESS)
    server.listen()
    print(f"[LISTENING] Server is listening on {LOCAL_IP} on PORT:{port}")

    while True:
        # This will block the code until a connection is made
        connection, address = server.accept()
        thread = threading.Thread(target=connectClient, args=(connection, address))
        thread.start()
        print(f"[NUMBER OF CONNECTIONS]: {threading.active_count() - 1}")

if __name__ == "__main__":
    port = 8080
    startServer(port)