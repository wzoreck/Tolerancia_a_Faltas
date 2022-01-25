import json
import socket
import random
import requests


'''
Estrutura da Operação
operacao = {
    'id': 1,
    'operacao': 'debito/credito',
    'valor': 100,
}
'''


def requisita_transacao(transacao):
    print(transacao)


def main():
    saldo = 0.0
    transacao = {}

    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_cliente.bind(('127.0.0.1', random.randint(1000, 2000)))

    while True: 
        print('-------------------------------------------------')
        print(f'Saldo: R$ {saldo}\n')

        print('1 - Débito')
        print('2 - Crédito')

        escolha = input('Informe o número da operação desejada: ')
        valor = input('Informe o valor: ')

        try:
            valor = float(valor)

            if escolha == '1':
                saldo += valor
            elif escolha == '2':
                saldo -= valor
            else:
                print('Opção não disponível, tente novamente.')
        except:
            print('Valor inválido!')
    
        print('\n')

if __name__ == '__main__':
    main()