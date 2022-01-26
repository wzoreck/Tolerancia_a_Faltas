import json
import socket
import random
import settings


'''
Estrutura da Operação
operacao = {
    'id': 1,
    'operacao': 'debito/credito',
    'valor': 100,
}
'''


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



def main():
    saldo = 0.0
    id_atual = 1
    transacao = {}

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