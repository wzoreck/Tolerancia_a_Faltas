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
acordos = []


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


def notifica_processo(mensagem, destino):
    socket_notificacao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
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
    global acordos
    
    argumentos = sys.argv
    socket_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if 'principal' in argumentos:
        principal = True
        socket_replica.bind(('127.0.0.1', settings.PORTA_PRINCIPAL))
    else:
        porta = random.randint(2000, 3000)
        socket_replica.bind(('127.0.0.1', porta))
        notifica_processo(json.dumps({'nova_replica': porta}), ('127.0.0.1', settings.PORTA_PRINCIPAL))

    if 'traidor' in argumentos:
        traidor = True

    print('\nServidor iniciado, <Ctr + C> para pará-lo.')
    socket_replica.listen()
    
    while True:
        socket_cliente, endereco = socket_replica.accept()
        mensagem = socket_cliente.recv(1024)

        data_conexao = datetime.now()
        data_conexao = data_conexao.strftime('%d-%m-%Y %H:%M:%S')
        print('\n-------------------------------------------------')
        print(f'[{data_conexao}] - Nova conexão => {endereco[0]}:{endereco[1]}')

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
                    notifica_processo(json.dumps({'novo_saldo': novo_saldo, 'origem': porta}), ('127.0.0.1', settings.PORTA_PRINCIPAL))
                
            if not principal:
                if 'novo_saldo' in mensagem:
                    resultados.append(mensagem)
                    acordo = True
                    
                    print(f'Resultados recebidos: {resultados}')
                    
                    if len(resultados) == len(replicas) - 1:
                        for resultado in resultados:
                            if resultado['novo_saldo'] != novo_saldo:
                                print('FALHA: Não houve acordo!')
                                acordo = False
                                break
                            
                        notifica_processo(json.dumps({'acordo': acordo}), ('127.0.0.1', settings.PORTA_PRINCIPAL))
                        resultados = []     
            
            if 'acordo' in mensagem:
                print(f'Acordo: {mensagem}')
                acordos.append(mensagem)
                
                if len(acordos) == len(replicas):
                    acordo_aux = True
                    for acordo in acordos:
                        if not acordo['acordo']:
                            acordo_aux = False
                            break
                    
                    # Notifica usuário
                    resultado_final = {'status': acordo_aux}
                    if acordo_aux:
                        resultado_final['saldo_atualizado'] = novo_saldo
                        
                    notifica_processo(json.dumps(resultado_final), ('127.0.0.1', settings.PORTA_CLIENTE))
                    acordos = []
                    
        except:
            print('Não possível decodificar a mensagem!')
        
        
if __name__ == '__main__':
    main()
