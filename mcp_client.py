import socket

HOST = 'localhost'
PORT = 9091

def start_client():
    print("🔵 MCP Client started")
    print("Ask me anything (e.g., 'latest tech news' or 'movies released today')\nType 'exit' to quit.\n")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        while True:
            query = input("🧑 You: ")
            client.sendall(query.encode())
            if query.lower() == "exit":
                break
            response = client.recv(8192).decode()
            print(f"\n🤖 Server:\n{response}\n")

if __name__ == "__main__":
    start_client()
