import socket
import threading


def connect_client(connection,addreas):
    pass

def startServer():
    # Server Configuration
    PORT = 8080
    LOCAL_IP = socket.gethostbyname(socket.gethostname())# Get the IP address of the server 
    ADDREASE = (LOCAL_IP, PORT) 

    # Create a socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDREASE)
    server.listen()
    print(f"[LISTENING] Server is listening on {LOCAL_IP}on PORT:{PORT}")

    # Accept the connection from the client and create a thread to handle the connection
    while True:
        #this will block the code until a connection is made
        connection, addreas = server.accept()
        
        # Create a thread to handle the connection take the connection and the addreas as arguments
        thread = threading.Thread(target=connect_client, args=(connection,addreas))
        thread.start()
        print("[NEW CONNECTION FROM A CLIENT]")
        #Subtract the main thread from the active threads
        print(f"[NUMBER OF CONNECTIONS] {threading.activeCount() - 1}")

startServer()