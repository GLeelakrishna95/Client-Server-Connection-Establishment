import threading
import socket

alias = input('Enter your desired alias: ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# get the server's IP address automatically
host = socket.gethostname()
# specify the port number
port = 12345
# connect to the server
client.connect((host, port))


def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "alias?":
                client.send(alias.encode('utf-8'))
            elif message.startswith('/kick'):
                print('You have been kicked from the chat room.')
                client.close()
                break
            else:
                print(message)
        except ConnectionResetError:
            print('Server connection lost.')
            client.close()
            break
        except:
            print('Error!')
            client.close()
            break

def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "alias?":
                client.send(alias.encode('utf-8'))
            elif message.startswith('/kick'):
                print('You have been kicked from the chat room.')
                client.close()
                break
            else:
                print(message)
        except:
            print('Error!')
            client.close()
            break

def private_chat():
    while True:
        recipient = input("Enter recipient's alias: ")
        message = input("Enter your message: ")
        private_message = f'{alias} (private message): {message}'
        client.send(f'/private {recipient} {private_message}'.encode('utf-8'))


def client_send():
    while True:
        message = input()
        if message == '/exit':
            client.send(message.encode('utf-8'))
            client.close()
            break
        elif message.startswith('/private'):
            recipient, private_message = message.split(maxsplit=2)[1:]
            message = f'{alias} (private message): {private_message}'
            client.send(f'/private {recipient} {message}'.encode('utf-8'))
        else:
            message = f'{alias}: {message}'
            client.send(message.encode('utf-8'))





receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()



