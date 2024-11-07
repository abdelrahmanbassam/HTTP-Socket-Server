#initial code just to test the server
import socket
import sys

def sendGetRequest(server_ip, port, file_path):
    # Create a socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, port))
    test = f"GET {file_path} HTTP/1.1\r\nHost: {server_ip}\r\n\r\n"
    client.send(test.encode())
    client.close()

def sendPostRequest(server_ip, port, file_path):
    # Create a socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, port))
    test = f"GET {file_path} HTTP/1.1\r\nHost: {server_ip}\r\n\r\n"
    client.send(test.encode())
    client.close()

if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     print("Usage: python my_client.py <server_ip> <port> <GET|POST> <file_path>")
    #     sys.exit(1)

    # server_ip = sys.argv[1]
    # port = int(sys.argv[2])
    # command = sys.argv[3].upper() # GET or POST    python client.py 127.0.0.1 8080 POST /submit
    # file_path = sys.argv[4]
    server_ip = "192.168.1.20"
    port = 8080
    command = "GET"
    file_path = "/index.html"
    if command == "GET":
        sendGetRequest(server_ip, port, file_path)
    elif command == "POST":
        sendPostRequest(server_ip, port, file_path)
    else:
        print("Invalid command. Use GET or POST.")