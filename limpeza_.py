import re


def limpeza(texto):
    if re.findall('imaging', texto, re.IGNORECASE) or re.findall('imagem', texto, re.IGNORECASE):
        texto = ''
        texto = 'Imagem'
    if re.findall('belt', texto, re.IGNORECASE) or re.findall('cinto', texto, re.IGNORECASE):
        texto = ''
        texto = 'Belt'
    if re.findall('fusor', texto, re.IGNORECASE) or re.findall('fuser', texto, re.IGNORECASE):
        texto = ''
        texto = 'Fusor'
    if re.findall('yellow', texto, re.IGNORECASE) or re.findall('amarelo', texto, re.IGNORECASE):
        texto = ''
        texto = 'Amarelo'
    elif re.findall('cyan', texto, re.IGNORECASE) or re.findall('ciano', texto, re.IGNORECASE):
        texto = ''
        texto = 'Ciano'
    elif re.findall('magenta', texto, re.IGNORECASE):
        texto = ''
        texto = 'Magenta'
    elif re.findall('black', texto, re.IGNORECASE) or re.findall('preto', texto, re.IGNORECASE):
        texto = ''
        texto = 'Preto'

    return texto


def limpeza2(texto):
    encontra2pontos = texto.find(':')+2
    tamanhoLinha = len(texto)-1
    encontraAspas = texto.rfind('\"')
    texto = texto[encontra2pontos:tamanhoLinha]
    if encontraAspas != -1:
        texto = texto.replace('\"', "")
        texto = texto.replace(',', "")
        texto = texto.replace('S/N:"', "")
        texto = texto.replace('.', "")
        texto = texto.rstrip()
        texto = limpeza(texto)

    return texto


def conta_linha(arquivo):
    numLinhas = 0
    contador = []
    resultado = ""
    with open(arquivo, 'r') as file:
        for linha in file:
            linha = limpeza2(linha)
            a = len(linha)
            if a != 0:
                contador.append(linha)
                numLinhas += 1

    for itens in contador:
        resultado += f"{itens}, "

    return numLinhas, contador, resultado


a = conta_linha(input('File: '))
b = len(a[1])
print(b)
print(a[2])
