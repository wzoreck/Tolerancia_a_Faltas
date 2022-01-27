import json
import socket
import random
import settings
from threading import Thread


'''
Estrutura da Operação
operacao = {
    'id': 1,
    'operacao': 'debito/credito',
    'valor': 100,
}
'''
saldo = 0.0



def requisita_transacao(transacao):
    transacao = json.dumps(transacao).encode('UTF-8')
    
    try: 
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.bind(('127.0.0.1', random.randint(1000, 2000)))
        
        destino = ('127.0.0.1', settings.PORTA_PRINCIPAL)
        socket_cliente.connect(destino)
        socket_cliente.send(transacao)

        socket_cliente.close()
        return True
    except:
        return False


def thread_escuta(socket_thread):
    global saldo
    socket_thread.listen()
    
    while True:
        socket_principal, endereco = socket_thread.accept()
        mensagem = socket_principal.recv(1024)
        mensagem = json.loads(mensagem.decode('UTF-8'))
        if mensagem['status']:
            try:
                saldo = float(mensagem['saldo_atualizado'])
                print('-------------------------------------------------')
                print(f'Saldo: R$ {saldo}\n')
            except:
                print('Erro ao atualizar saldo!')
        else:
            print('\nTransacão não realizada!')
        
        # print(mensagem)

def main():
    global saldo
    id_atual = 1
    transacao = {}

    socket_resultado = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_resultado.bind(('127.0.0.1', settings.PORTA_CLIENTE))
    
    Thread(target=thread_escuta, args=[socket_resultado]).start()

    while True: 
        print('-------------------------------------------------')
        print(f'Saldo: R$ {saldo}\n')

        print('1 - Débito')
        print('2 - Crédito')

        escolha = input('Informe o número da operação desejada: ')
        valor = input('Informe o valor: ')

        try:
            valor = float(valor)

            transacao = {
                'id': id_atual,
                'valor': valor,
                'saldo': saldo,
            }

            if escolha == '1':
                transacao['operacao'] = 'debito'
                requisita_transacao(transacao)
            elif escolha == '2':
                transacao['operacao'] = 'credito'
                requisita_transacao(transacao)
            else:
                print('Opção não disponível, tente novamente.')


            id_atual += 1
        except:
            print('Valor inválido!')
    
        print('\n')

if __name__ == '__main__':
    main()