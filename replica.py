import sys
import json
import socket
import random
import settings
from datetime import datetime


traidor = False
replicas = []
porta = 0


def validar_operacao(operacao):
    novo_saldo = 0
    if traidor:
        if operacao['operacao'] == 'debito':
            novo_saldo =  operacao['saldo'] + operacao['valor']
        if operacao['operacao'] == 'credito':
            novo_saldo = operacao['saldo'] - operacao['valor']
    else:
        if operacao['operacao'] == 'debito':
            novo_saldo = operacao['saldo'] - operacao['valor']
        if operacao['operacao'] == 'credito':
            novo_saldo = operacao['saldo'] + operacao['valor']
    
    print(f'Novo saldo: {novo_saldo}')
    
    envia_mensagem_replicas(json.dumps(operacao))

def notifica_criacao_replica(porta):
    socket_notificacao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = ('127.0.0.1', settings.PORTA_PRINCIPAL)
    mensagem = json.dumps({'nova_replica': porta})
    try:
        socket_notificacao.connect(destino)
        socket_notificacao.send(mensagem.encode('UTF-8'))
        socket_notificacao.close()
    except:
        print('Erro ao notificar criacao de réplica!')

def envia_mensagem_replicas(mensagem):
    for replica in replicas:
        if not replica == porta:
            socket_notificacao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            destino = ('127.0.0.1', replica)
            
            try:
                socket_notificacao.connect(destino)
                socket_notificacao.send(mensagem.encode('UTF-8'))
            except:
                print('Erro ao notificar réplicas!')
            
            socket_notificacao.close()
            

def main():
    argumentos = sys.argv
    socket_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if 'principal' in argumentos:
        socket_replica.bind(('127.0.0.1', settings.PORTA_PRINCIPAL))
    else:
        porta = random.randint(2000, 3000)
        socket_replica.bind(('127.0.0.1', porta))
        notifica_criacao_replica(porta)

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

            if 'nova_replica' in mensagem:
                print(f'Nova réplica: {mensagem["nova_replica"]}')
                replicas.append(mensagem["nova_replica"])
                envia_mensagem_replicas(json.dumps({'replicas': replicas}))
            
            if 'replicas' in mensagem:
                for replica in mensagem['replicas']:
                    if not replica in replicas:
                        replicas.append(replica)
                
                print(f'Replicas: {replicas}')

            if 'operacao' in mensagem:
                validar_operacao(mensagem)
        except:
            print('Não possível decodificar a mensagem!')
        

if __name__ == '__main__':
    main()
