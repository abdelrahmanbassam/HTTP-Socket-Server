import socket
import time
import threading
import numpy as np
import matplotlib.pyplot as plt

SERVER_IP = socket.gethostbyname(socket.gethostname())
file_path = "txtserver.txt"
SERVER_PORT = 8080
NUM_REQUESTS = 10
CHUNK_SIZE = 1024

def client_task(response_times, client_id):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_IP, SERVER_PORT))
        total_time = 0
        
        for i in range(NUM_REQUESTS):
            start = time.time()
            keep_alive = i < NUM_REQUESTS - 1
            connection_header = "keep-alive" if keep_alive else "close"
            request = f"GET /{file_path} HTTP/1.1\r\nHost: {SERVER_IP}\r\nConnection: {connection_header}\r\n\r\n".encode()
            client.sendall(request)
            response = client.recv(CHUNK_SIZE)
            end = time.time()
            
            total_time += (end - start)
        
        average_time = (total_time / NUM_REQUESTS) * 1000 # in ms
        response_times[client_id] = average_time
        client.close()
    except Exception as e:
        print(f"Client {client_id} error: {e}")

def test_server_performance(client_counts):
    results = []
    for num_clients in client_counts:
        threads = []
        response_times = [0] * num_clients
        
        for i in range(num_clients):
            thread = threading.Thread(target=client_task, args=(response_times, i))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        average_response_time = np.mean(response_times)
        results.append(average_response_time)
        print(f"Average response time for {num_clients} clients: {average_response_time:.4f} ms")
    
    return results

if __name__ == "__main__":
    client_counts = [1, 5, 10, 20, 50, 100]
    average_response_times = test_server_performance(client_counts)

    plt.figure(figsize=(10, 6))
    plt.plot(client_counts, average_response_times, marker='o', color='b')
    plt.title("Server Performance with Increasing Clients")
    plt.xlabel("Number of Clients")
    plt.ylabel("Average Response Time (ms)")
    plt.grid(True)
    plt.show()
