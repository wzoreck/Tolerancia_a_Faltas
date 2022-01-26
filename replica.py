import sys
import json
import socket
import random
import settings
from datetime import datetime

principal = False
traidor = False
replicas = []
porta = 0
novo_saldo = 0
resultados = []


def validar_operacao(operacao):
    global novo_saldo
    global traidor
    
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

def notifica_principal(mensagem):
    socket_notificacao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = ('127.0.0.1', settings.PORTA_PRINCIPAL)
    
    try:
        socket_notificacao.connect(destino)
        socket_notificacao.send(mensagem.encode('UTF-8'))
        socket_notificacao.close()
    except:
        print('Erro ao notificar processo principal!')

def envia_mensagem_replicas(mensagem):
    global replicas
    
    for replica in replicas:
        if not replica == porta:
            socket_replicacao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            destino = ('127.0.0.1', replica)
            
            try:
                socket_replicacao.connect(destino)
                socket_replicacao.send(mensagem.encode('UTF-8'))
            except:
                print('Erro ao notificar réplicas!')
            
            socket_replicacao.close()
            

def main():
    global principal
    global novo_saldo
    global porta
    global traidor
    global replicas
    global resultados
    
    argumentos = sys.argv
    socket_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if 'principal' in argumentos:
        principal = True
        socket_replica.bind(('127.0.0.1', settings.PORTA_PRINCIPAL))
    else:
        porta = random.randint(2000, 3000)
        socket_replica.bind(('127.0.0.1', porta))
        notifica_principal(json.dumps({'nova_replica': porta}))

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
                if principal:
                    envia_mensagem_replicas(json.dumps(mensagem))
                else:
                    envia_mensagem_replicas(json.dumps({'novo_saldo': novo_saldo, 'origem': porta}))
                    notifica_principal(json.dumps({'novo_saldo': novo_saldo, 'origem': porta}))
                    
            if 'novo_saldo' in mensagem:
                resultados.append(mensagem)
                
                if len(resultados) == len(replicas) - 1:
                    for resultado in resultados:
                        if resultado['novo_saldo'] == novo_saldo:
                            pass
                        else:
                            pass
            
            print(resultados)
                    
        except:
            print('Não possível decodificar a mensagem!')
        

if __name__ == '__main__':
    main()
