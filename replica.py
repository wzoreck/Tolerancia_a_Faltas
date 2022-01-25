import sys
import json
import socket
import random


PORTA_PRINCIPAL = 6060
traidor = False


def main():
    argumentos = sys.argv
    print(argumentos)

    socket_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if 'traira' in argumentos:
        traidor = True
        socket_replica.bind(('127.0.0.1', PORTA_PRINCIPAL))
    else:
        socket_replica.bind(('127.0.0.1', random.randint(2000, 3000)))

    socket_replica.listen()
    
    socket_cliente, endereco = socket_replica.accept()
    mensagem = socket_cliente.recv(1024)

    while True:
        print(f'Cliente conectado => {endereco[0]}:{endereco[1]}')

        socket_cliente, endereco = socket_replica.accept()
        mensagem = socket_cliente.recv(1024)

if __name__ == '__main__':
    main()
