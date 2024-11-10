# Simple HTTP Web Server and Client

# Simple HTTP Web Server and Client

### Contributors

- **Mourad Mahgoub Abdelsalam 21011303**
- **Abdelrahman Bassam Elsayed 21010729**

## Introduction

This project implements a basic HTTP server and client using socket programming in Python. The server handles HTTP GET and POST requests, supporting multi-threaded handling and persistent connections. The client sends HTTP requests based on commands from a file, and the performance analyzer evaluates the server’s response time under varying client loads.

## Project Structure

- `server.py`: Multi-threaded HTTP server handling GET and POST requests.
- `client.py`: HTTP client that processes commands to send GET or POST requests to the server.
- `performance.py`: Performance evaluation module that measures server response times with varying numbers of concurrent clients.

## Constants Used

- **`CHUNK_SIZE = 1024`**: Sets the size of each data chunk sent or received over the network in bytes.
- **`DEFAULT_TIMEOUT = 10`**: Sets the default timeout duration in seconds for client connections.

## Server.py

### Overview

The `server.py` file sets up a multi-threaded HTTP server, allowing it to handle multiple client connections simultaneously. Each client connection is managed in a separate thread, and the server handles GET and POST requests for text, HTML, and image files.

1. **Starting the Server**

The `startServer` function initializes the server, listens for incoming connections, and starts a new thread for each client connection.

```python
def startServer(port=8080):
    LOCAL_IP = socket.gethostbyname(socket.gethostname())
    ADDRESS = (LOCAL_IP, port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDRESS)
    server.listen()
    print(f"[LISTENING] Server is listening on {LOCAL_IP} on PORT:{port}")
    while True:
        connection, address = server.accept()
        thread = threading.Thread(target=connectClient, args=(connection, address))
        thread.start()
```

1. **Connecting with a Client**

The `connectClient` function manages individual client connections, parses HTTP requests, and invokes the appropriate request handler based on the HTTP method. Adjusts timeout based on active connections.

```python
def connectClient(connection, address):
    print(f"[New Connection] from {address} has been established!")
    isConnected = True
    
    while isConnected:
        try:
            # Dynamically adjust the timeout
            active_connections = threading.active_count() - 1
            timeout = max(DEFAULT_TIMEOUT / (active_connections + 1), 1)
            connection.settimeout(timeout)
            #a lot of pasring ,, look in the server.py for detials 
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
```

1. **Handling GET Requests**

The `getRequestHandler` function manages file retrievals for GET requests. It searches for the requested file and responds with either the file data or a 404 error.

```python
def getRequestHandler(connection, filePath):
    if os.path.exists(filePath):
        with open(filePath, 'rb') as file:
            data = file.read()
        response = b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(data)).encode() + b"\r\n\r\n" + data
    else:
        response = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"        
        response += b"<html><body><h1>404 Not Found</h1></body></html>"    
        connection.send(response)
```

1. **Handling POST Requests**

The `postRequestHandler` function manages file uploads by writing the uploaded data to a specified file.

```python
def postRequestHandler(connection, filePath, data):
    with open(filePath, 'wb') as file:
        file.write(data)
    response = b"HTTP/1.1 201 Created\r\nContent-Type: text/html\r\n\r\n"    
    response += b"<html><body><h1>File Created</h1></body></html>"    
    connection.send(response)
```

## client.py

### Overview

The `client.py` file acts as an HTTP client that reads commands from a file to perform GET and POST requests to a server. Each command specifies the type of operation and the file path.

### Functions

1. **`processCommands(command_file)`**
    - Reads and executes commands from a file.
    - Opens `command_file`, reads each command, and splits it to determine the type (`client_get` or `client_post`), file path, and other details. For each command, it either calls `sendGetRequest` or `sendPostRequest`, using ‘keep-alive’ connections when appropriate to maintain a persistent connection for sequential commands.
    
    ```python
    def processCommands(command_file):
        with open(command_file, 'r') as file:
            commands = file.readlines()
        server_ip = socket.gethostbyname(socket.gethostname())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((server_ip, DEFAULT_PORT))
            for command in commands:
                parts = command.strip().split()
                cmd_type = parts[0]
                file_path = parts[1]
                keep_alive = (i < len(commands) - 1)
                if cmd_type == "client_get":
                    sendGetRequest(client, file_path, keep_alive)
                elif cmd_type == "client_post":
                    sendPostRequest(client, file_path, keep_alive)
    ```
    
2. **`sendGetRequest(client, file_path, keep_alive=True)`**
    - Sends a GET request to retrieve a file from the server.
    - Constructs a GET request, sets the `Connection` header based on `keep_alive`, and sends it to the server. Receives the response in chunks and saves the file data locally. If the file is found, it saves it locally; otherwise, it handles error responses.
    
    ```python
    def sendGetRequest(client, file_path, keep_alive=True):
        connection_header = "keep-alive" if keep_alive else "close"
        request = f"GET /{file_path} HTTP/1.1\r\nHost: {client.getsockname()[0]}\r\nConnection: {connection_header}\r\n\r\n".encode()
        client.send(request)
        response = b""
        while True:
            part = client.recv(CHUNK_SIZE)
            if not part:
                break
            response += part
            if b"\r\n\r\n" in response:
                break
    
        header, data = response.split(b"\r\n\r\n", 1)
        content_length = int(header.decode().split("Content-Length: ")[1].split("\r\n")[0]) if "Content-Length: " in header.decode() else 0
        while len(data) < content_length:
            data += client.recv(CHUNK_SIZE)
        print(header.decode())
        with open(file_path, 'wb') as file:
            file.write(data)
    ```
    
3. **`sendPostRequest(client, file_path, keep_alive=True)`**
    - Sends a POST request to upload a file to the server.
    - Reads the file content from `file_path`, constructs a POST request with the file content in the body, and sends it to the server. The connection header is set based on `keep_alive`, allowing for persistent connections if needed.
    
    ```python
    def sendPostRequest(client, file_path, keep_alive=True):
        connection_header = "keep-alive" if keep_alive else "close"    with open(file_path, 'rb') as file:
            data = file.read()
        request = f"POST /{file_path} HTTP/1.1\r\nHost: {client.getsockname()[0]}\r\nContent-Length: {len(data)}\r\nConnection: {connection_header}\r\n\r\n".encode() + data
        client.send(request)
        response = client.recv(CHUNK_SIZE)
        print(response.decode())
    ```
    

## performance.py

### Overview

The `performance.py` file evaluates server response times under different loads by measuring how the server handles an increasing number of concurrent clients. Each client sends multiple GET requests, and the performance results provide insight into server scalability.

### Functions

1. **`client_task(response_times, client_id)`**
    - Simulates a single client that sends multiple GET requests to the server and records response times.
    - Creates a connection to the server, sends multiple GET requests, and measures the time taken for each. Computes the average response time per client and stores it in `response_times` for later analysis.
    
    ```python
    def client_task(response_times, client_id):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_IP, SERVER_PORT))
        total_time = 0    for i in range(NUM_REQUESTS):
            start = time.time()
            keep_alive = i < NUM_REQUESTS - 1        request = f"GET /{file_path} HTTP/1.1\r\nHost: {SERVER_IP}\r\nConnection: {'keep-alive' if keep_alive else 'close'}\r\n\r\n".encode()
            client.sendall(request)
            client.recv(CHUNK_SIZE)
            end = time.time()
            total_time += (end - start)
        response_times[client_id] = (total_time / NUM_REQUESTS) * 1000  # Convert to milliseconds    client.close()
    ```
    
2. **`test_server_performance(client_counts)`**
    - Tests the server’s performance by simulating various numbers of concurrent clients.
    - For each client count in `client_counts`, creates and starts multiple client threads, each running `client_task`. After all threads complete, calculates the average response time across all clients and appends it to the results. This gives a performance overview for different client loads.
    
    ```python
    def test_server_performance(client_counts):
        results = []
        for num_clients in client_counts:
            response_times = [0] * num_clients
            threads = [threading.Thread(target=client_task, args=(response_times, i)) for i in range(num_clients)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            average_response_time = np.mean(response_times)
            results.append(average_response_time)
            print(f"Average response time for {num_clients} clients: {average_response_time:.4f} ms")
        return results
    ```
    

## How To Use

1. Step 1: start server from [server.py](http://server.py) and type the port number
    
    ![image.png](assets/image.png)
    
    ![image.png](assets/image%201.png)
    
2. Step 2 : run the [client.py](http://client.py) to make it send requests to server ,the client reads commands from commands.txt file and send these requests to server.
    
    ![image.png](assets/image%202.png)
    
- server side:
    
    ![image.png](assets/image%203.png)
    
    - as we see here the server make a new connection from IP= 192.168.1.20 and port=63110
    - displaying number of connection which is 1 (since we run one client)
    - and displaying the 3 get requests , 3 post request
- client side:
    
    ![image.png](assets/image%204.png)
    
    - First: receiving responses from the serverof the 3 get requests , each one with different content-length
    - receiving responses from the server of the 3 Post requests

**After making these requests ,, we can see new files arrived in both client and server due to get and post requests** 

- client side got 3 new files(files with  green color) with different types(txt,png and html)
    
    ![image.png](assets/image%205.png)
    

- same happened in server side:
    
    ![image.png](assets/image%206.png)
    

if we try to get a file and it’s not in the server side we will get error message 

![image.png](assets/image%207.png)

![image.png](assets/image%208.png)

## Bonus Part :

### 1-Testing the server with a real web browser

open the browser then write the server IP and port number (8080) in the url like this :
http://192.168.1.20:8080/server.html

and get .png, .html, or .txt

![image.png](assets/image%209.png)

 

### 2-Performance Evaluation

![image.png](assets/image%2010.png)

![image.png](assets/image%2011.png)