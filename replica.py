import sys
import json
import socket
import random
import settings
from datetime import datetime


traidor = False
replicas = []


def validar_operacao(operacao):
    return True


def main():
    argumentos = sys.argv
    socket_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if 'principal' in argumentos:
        socket_replica.bind(('127.0.0.1', settings.PORTA_PRINCIPAL))
    else:
        socket_replica.bind(('127.0.0.1', random.randint(2000, 3000)))

    if 'traidor' in argumentos:
        traidor = True

    print('Servidor iniciado, <Ctr + C> para pará-lo.')
    socket_replica.listen()
    
    while True:
        socket_cliente, endereco = socket_replica.accept()
        mensagem = socket_cliente.recv(1024)

        data_conexao = datetime.now()
        data_conexao = data_conexao.strftime('%d-%m-%Y %H:%M:%S')
        print(f'[{data_conexao}] - Cliente conectado => {endereco[0]}:{endereco[1]}')

        try:
            mensagem = mensagem.decode('UTF-8')
            mensagem = json.loads(mensagem)

            validar_operacao(mensagem)
        except:
            print('Não possível decodificar a mensagem!')
        

if __name__ == '__main__':
    main()
