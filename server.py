import threading
import socket
import sys

# get the local machine name
host = socket.gethostname()

# specify a port for your service
port = 12345
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
server.bind((host, port))
server.listen()
clients = []
aliases = []

# Function to print server log messages
def server_log(message):
    print(f"[SERVER] {message}")
    
# Function to send a private message to a specific client
def send_private_message(sender_alias, recipient_alias, message):
    if recipient_alias in aliases:
        # Get the index of the recipient client
        recipient_index = aliases.index(recipient_alias)
        recipient_client = clients[recipient_index]
        sender_alias_formatted = sender_alias + ' (private message): '
        private_message = sender_alias_formatted.encode('utf-8') + message.encode('utf-8')
        recipient_client.send(private_message)
    else:
        sender_client = clients[aliases.index(sender_alias)]
        sender_client.send('Recipient alias not found'.encode('utf-8'))
def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            client.send(message)

# Function to handle clients' connections
def handle_client(client):
    while True:
        try:
            server_log("Waiting to receive data from client")
            message = client.recv(1024)
            server_log(f"Received data from client: {message}")
            if message.decode('utf-8').startswith('/kick'):
                # Parse the alias of the client to be kicked
                kick_alias = message.decode('utf-8').split(' ')[1]
                if kick_alias in aliases:
                    # Get the index of the client to be kicked
                    kick_index = aliases.index(kick_alias)
                    # Kick the client and remove their alias from the list
                    kick_client = clients[kick_index]
                    kick_client.send('You have been kicked from the chat room'.encode('utf-8'))
                    kick_client.close()
                    aliases.remove(kick_alias)
                    clients.remove(kick_client)
                    broadcast(f'{kick_alias} has been kicked from the chat room'.encode('utf-8'))
                else:
                    client.send('Alias not found'.encode('utf-8'))
            elif message.decode('utf-8').startswith('/stop'):
                broadcast('Server is shutting down...'.encode('utf-8'))
                for client in clients:
                    client.close()
                server.close()
                sys.exit(0)
            elif message.decode('utf-8').startswith('/private'):
                # Parse the recipient alias and message from the command
                recipient_alias, private_message = message.decode('utf-8').split(' ', 2)[1:]
                send_private_message(aliases[clients.index(client)], recipient_alias, private_message)
            else:
                  broadcast(message, sender=client)
        except ConnectionResetError:
            server_log(f"ConnectionResetError: {client}")
            break
        except ConnectionAbortedError:
            server_log(f"ConnectionAbortedError: {client}")
            break
        except socket.error as e:
            server_log(f"socket error: {e}")
            break
        except:
            server_log(f"Unexpected error: {sys.exc_info()[0]}")
            break

    index = clients.index(client)
    clients.remove(client)
    client.close()
    alias = aliases[index]
    broadcast(f'{alias} has left the chat room!'.encode('utf-8'))
    aliases.remove(alias)

# Main function to receive the clients' connections
def receive():
    server_log("Server is running and listening...")
    while True:
        client, address = server.accept()
        server_log(f"Connection is established with {str(address)}")
        client.send('alias?'.encode('utf-8'))
        alias = client.recv(1024)
        aliases.append(alias.decode('utf-8'))
        clients.append(client)
        server_log(f"The alias of this client is {alias.decode('utf-8')}")
        broadcast(f'{alias.decode("utf-8")} has connected to the chat room'.encode('utf-8'))
        client.send('You are now connected!'.encode('utf-8'))
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()
if __name__ == "__main__":
    server_log("Starting server...")
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    # Main thread listens for console input
    while True:
        try:
            command = input().strip()
            if command == '/stop':
                broadcast('Server is shutting down'.encode('utf-8'))
                for client in clients:
                    client.close()
                server.close()
                sys.exit(0)

        except KeyboardInterrupt:
            broadcast('Server is shutting down')
            for client in clients:
                client.close()
            server.close()
            sys.exit(0)