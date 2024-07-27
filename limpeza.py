import re
import sqlite3
import glob
from datetime import datetime


def tempo():
    now = datetime.now()
    return [now.strftime('%d-%m-%Y'), now.strftime('%H:%M')]


def formata_texto(texto):
    mapeamento = {
        'imaging': 'Imagem',
        'imagem': 'Imagem',
        'belt': 'Belt',
        'cinto': 'Belt',
        'fusor': 'Fusor',
        'fuser': 'Fusor',
        'yellow': 'Amarelo',
        'amarelo': 'Amarelo',
        'cyan': 'Ciano',
        'ciano': 'Ciano',
        'magenta': 'Magenta',
        'black': 'Preto',
        'preto': 'Preto'
    }
    for chave, valor in mapeamento.items():
        if re.search(chave, texto, re.IGNORECASE):
            return valor
    return texto


def limpa_texto(texto):
    caracteres_a_remover = ['"', ',', 'S/N:', '.']
    texto = texto.partition(':')[2].rstrip()
    texto = re.sub('|'.join(map(re.escape, caracteres_a_remover)), '', texto)
    return formata_texto(texto)


def conta_linha(arquivo):
    with open(arquivo, 'r') as file:
        linhas = [formata_texto(linha) for linha in file]
    return len(linhas), linhas


def calcula(n1, n2):
    if n2 <= 0:
        return 0
    return int(n1 / n2 * 100)


def refina_lista(arquivo):
    num_linhas, linhas = conta_linha(arquivo)
    serial_number = linhas[0]
    razao_supr = num_linhas // 3

    lista_supr = [linhas[i:i + razao_supr]
                  for i in range(1, num_linhas, razao_supr)]

    if len(lista_supr) > 2:
        lista_supr_a = list(map(int, lista_supr[1]))
        lista_supr_b = list(map(int, lista_supr[2]))
        calculo_supr = [calcula(n1, n2)
                        for n1, n2 in zip(lista_supr_a, lista_supr_b)]

        lista_supr = [item for sublist in lista_supr for item in sublist]
        lista_supr.append(calculo_supr)
        lista_supr.insert(0, tempo() + [arquivo.rstrip('.txt'), serial_number])

    return lista_supr


def refina_banco(lista):
    dados = {'Preto': None, 'Ciano': None, 'Magenta': None,
             'Amarelo': None, 'Fusor': None, 'Imagem': None, 'Belt': None}

    for item, valor in zip(lista[1], lista[2]):
        if item in dados:
            dados[item] = valor

    return (lista[0][0], lista[0][1], lista[0][2], dados['Preto'], dados['Ciano'], dados['Magenta'], dados['Amarelo'], dados['Fusor'], dados['Imagem'], dados['Belt'], lista[0][3])


def grava_bd():
    database = "bd_impressoras.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    cur.execute('''UPDATE equipamentos SET ip = NULL''')
    print('Coluna IP redefinida no Database')

    for arquivo in glob.glob('*.txt'):
        lista = refina_lista(arquivo)
        dados = refina_banco(lista)
        cur.execute('''UPDATE equipamentos SET data = ?, hora = ?, ip = ?, k = ?, c = ?, m = ?, y = ?, fusor = ?, imagem = ?, belt = ? WHERE serial LIKE ?''',
                    dados)
        print(f'{dados[-1]} = Registro gravado no Database')
        conn.commit()

    conn.close()


if __name__ == '__main__':
    grava_bd()
