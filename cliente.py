import json
import requests


'''
Estrutura da Operação
operacao = {
    'id': 1,
    'operacao': 'debito/credito',
    'valor': 100,
}
'''

while True: 
    print('1 - Débito')
    print('2 - Crédito')

    escolha = input('Informe o número da operação desejada: ')
    
    if escolha == '1':
        print('Débito')
    elif escolha == '2':
        print('Crédito')
    else:
        print('Opção não disponível, tente novamente.')
