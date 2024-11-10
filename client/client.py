import socket
import sys
import os

CHUNK_SIZE = 1024
DEFAULT_PORT = 8080

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

def sendPostRequest(client, file_path, keep_alive=True):
    connection_header = "keep-alive" if keep_alive else "close"
    file_path = file_path.lstrip("/")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, 'rb') as file:
        data = file.read()
    request = f"POST /{file_path} HTTP/1.1\r\nHost: {client.getsockname()[0]}\r\nContent-Length: {len(data)}\r\nConnection: {connection_header}\r\n\r\n".encode() + data
    client.send(request)
    response = client.recv(CHUNK_SIZE)
    print(response.decode())

def processCommands(command_file):
    with open(command_file, 'r') as file:
        commands = file.readlines()
    
    server_ip = socket.gethostbyname(socket.gethostname())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((server_ip, DEFAULT_PORT))
        
        for i, command in enumerate(commands):
            parts = command.strip().split()
            if len(parts) < 3:
                print(f"Invalid command: {command}")
                continue
            cmd_type = parts[0]
            file_path = parts[1]
            host_name = parts[2]
            port = int(parts[3]) if len(parts) > 3 else DEFAULT_PORT
            
            keep_alive = i < len(commands) - 1  
            
            if cmd_type == "client_get":
                sendGetRequest(client, file_path, keep_alive)
            elif cmd_type == "client_post":
                sendPostRequest(client, file_path, keep_alive)
            else:
                print(f"Unknown command: {cmd_type}")

if __name__ == "__main__":
    command_file = "commands.txt" 
    processCommands(command_file)