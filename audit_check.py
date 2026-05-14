#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict

REQUIRED_COLUMNS = [
    'Hora',
    'Nombre completo del usuario',
    'Usuario afectado',
    'Contexto del evento',
    'Componente',
    'Nombre evento',
    'Descripción',
    'Origen',
    'Dirección IP',
]


def normalize(value):
    if value is None:
        return ''
    return str(value).strip()


def load_rows(csv_path):
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError('El CSV no contiene cabecera.')

        available = set(reader.fieldnames)
        missing = [col for col in REQUIRED_COLUMNS if col not in available]
        if missing:
            raise ValueError(
                'Faltan columnas requeridas: ' + ', '.join(missing)
            )

        rows = []
        for row in reader:
            rows.append({col: normalize(row.get(col)) for col in REQUIRED_COLUMNS})
        return rows


def check_single_user_single_ip(rows):
    user_to_ips = defaultdict(set)
    for row in rows:
        user = row['Nombre completo del usuario']
        ip = row['Dirección IP']
        if user and ip:
            user_to_ips[user].add(ip)

    offenders = {user: sorted(ips) for user, ips in user_to_ips.items() if len(ips) > 1}

    print('1. Verificar que el mismo nombre de usuario no haya utilizado la misma IP')
    if not offenders:
        print('OK: cada usuario ha usado una única IP distinta o no hay datos suficientes.')
    else:
        print('FALLA: hay usuarios que han utilizado varias IPs:')
        for user in sorted(offenders):
            print(f'  - {user}: {", ".join(offenders[user])}')
    print()


def check_single_ip_single_user(rows):
    ip_to_users = defaultdict(set)
    for row in rows:
        user = row['Nombre completo del usuario']
        ip = row['Dirección IP']
        if user and ip:
            ip_to_users[ip].add(user)

    offenders = {ip: sorted(users) for ip, users in ip_to_users.items() if len(users) > 1}

    print('2. Verificar que la misma IP no haya sido usada por varios usuarios')
    if not offenders:
        print('OK: ninguna IP ha sido compartida por varios usuarios o no hay datos suficientes.')
    else:
        print('FALLA: hay IPs compartidas por varios usuarios:')
        for ip in sorted(offenders):
            print(f'  - {ip}: {", ".join(offenders[ip])}')
    print()


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} <ruta_csv>', file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]

    try:
        rows = load_rows(csv_path)
    except Exception as exc:
        print(f'Error al cargar el CSV: {exc}', file=sys.stderr)
        sys.exit(2)

    check_single_user_single_ip(rows)
    check_single_ip_single_user(rows)


if __name__ == '__main__':
    main()
