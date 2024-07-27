import os
import sys
import time
import subprocess

# Configurações
ips = [
    "10.20.22.11", "10.20.22.12", "10.20.22.13", "10.20.22.14", "10.20.22.15",
    "10.20.22.16", "10.20.22.17", "10.20.22.27", "10.20.22.28", "10.20.22.29",
    "10.20.22.30", "10.20.22.33", "10.20.22.34", "10.20.22.35", "10.20.22.36",
    "10.20.22.37", "10.20.22.38", "10.20.22.41", "10.20.22.42", "10.20.22.43",
    "10.20.22.44", "10.20.22.45", "10.20.22.48", "10.20.22.49", "10.20.22.50",
    "10.20.22.51", "10.20.22.54", "10.20.22.55", "10.20.22.56", "10.20.22.59",
    "10.20.22.60", "10.20.22.61", "10.20.22.62", "10.20.22.63", "10.20.22.64",
    "10.20.22.65", "10.20.22.66", "10.20.22.67", "10.20.22.68", "10.20.22.69",
    "10.20.22.70", "10.20.22.71", "10.20.22.73", "10.20.22.74", "10.20.22.75",
    "10.20.22.78", "10.20.22.79", "10.20.22.80", "10.20.22.81", "10.20.22.82",
    "10.20.22.83", "10.20.22.84", "10.20.22.85", "10.20.22.86", "10.20.22.87",
    "10.20.22.89", "10.20.22.90", "10.20.22.91", "10.20.22.92", "10.20.22.93",
    "10.20.22.94", "10.20.22.97", "10.20.22.98", "10.20.22.99", "10.20.22.100",
    "10.20.22.101", "10.20.22.102", "10.20.22.103", "10.20.22.104", "10.20.22.105",
    "10.20.22.108", "10.20.22.109", "10.20.22.111", "10.20.22.113"
]

centralizadores = [
    "10.20.22.20", "10.20.22.27", "10.20.22.87", "10.20.22.88",
    "10.20.22.93", "10.20.22.99", "10.20.22.101"
]


def converter(segundos):
    """Converte segundos em uma string no formato 'MM:SS'"""
    segundos %= 86400  # Segundos em um dia
    horas = segundos // 3600
    segundos %= 3600
    minutos = segundos // 60
    segundos %= 60
    return f'{minutos:02d}:{segundos:02d}'


def checar_arquivo(arquivo):
    """Remove um arquivo se ele existir"""
    if os.path.exists(arquivo):
        os.remove(arquivo)


def snmp(ip):
    """Executa comandos SNMP e salva a saída em um arquivo"""
    comandos = [
        # Serial Number
        f'snmpwalk -v1 -Oav -t1 -c public -r5 {
            ip} iso.3.6.1.2.1.43.5.1.1.17.1 >> {ip}.txt',
        # Dispositivos
        f'snmpwalk -v1 -Oav -t1 -c public -r5 {
            ip} iso.3.6.1.2.1.43.11.1.1.6.1 >> {ip}.txt',
        # Capacidade utilizada
        f'snmpwalk -v1 -Oav -t1 -c public -r5 {
            ip} iso.3.6.1.2.1.43.11.1.1.9.1 >> {ip}.txt',
        # Capacidade total
        f'snmpwalk -v1 -Oav -t1 -c public -r5 {
            ip} iso.3.6.1.2.1.43.11.1.1.8.1 >> {ip}.txt'
    ]
    for comando in comandos:
        subprocess.run(comando, shell=True, check=True)


def status(centralizador):
    """Executa comando SNMP para verificar status do centralizador"""
    comando = f'snmpwalk -v1 -Oav -t1 -c public -r5 {
        centralizador} iso.3.6.1.2.1.43.16.5.1.2.1 >> TESTE_{centralizador}.txt'
    subprocess.run(comando, shell=True, check=True)


def ping(ip):
    """Executa um ping no IP e retorna se o IP está ativo"""
    resultado = subprocess.run(
        ['ping', '-c5', '-q', ip], stdout=subprocess.DEVNULL)
    return resultado.returncode == 0


def coleta():
    """Executa a coleta de dados dos IPs fornecidos"""
    inicio = time.time()
    args = sys.argv[1:]  # Ignora o nome do script

    if len(args) == 0:
        ips_a_verificar = centralizadores
    elif len(args) == 1:
        ips_a_verificar = [args[0]]
    else:
        print("Uso: script.py [IP]")
        sys.exit(1)

    nao_respondentes = []
    for ip in ips_a_verificar:
        if ping(ip):
            checar_arquivo(f'{ip}.txt')
            print(f'+ {ip}')
            if ip in centralizadores:
                status(ip)
        else:
            print(f'- {ip}')
            nao_respondentes.append(ip)

    if nao_respondentes:
        print(f'{len(nao_respondentes)} de {len(ips_a_verificar)
                                            } IPs não responderam à coleta: {nao_respondentes}')

    fim = time.time()
    total = fim - inicio
    print(f'Tempo de execução: {converter(total)}')


if __name__ == '__main__':
    coleta()
