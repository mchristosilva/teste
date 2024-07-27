import sqlite3
from flask import Flask, render_template, request, redirect, url_for

# Configurações
DATABASE = 'bd_impressoras.db'

app = Flask(__name__)

# Consultas SQL
QUERIES = {
    'pesquisaFull': '''SELECT ip, serial, modelo, local, data, preto, ciano, magenta, amarelo, fusor, imagem, belt 
                       FROM INVENTARIO_TI_PRINTERS 
                       WHERE ip IS NOT NULL 
                       AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                       ORDER BY local ASC''',
    'pesquisaK': '''SELECT ip, serial, modelo, local, data, preto 
                    FROM INVENTARIO_TI_PRINTERS 
                    WHERE preto <= 5 
                    AND (modelo NOT LIKE '%C4010%' OR modelo NOT LIKE '%E57540%') 
                    AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                    ORDER BY preto DESC''',
    'pesquisaColor': '''SELECT ip, serial, modelo, local, data, preto, ciano, magenta, amarelo 
                        FROM INVENTARIO_TI_PRINTERS 
                        WHERE ip IS NOT NULL 
                        AND (modelo LIKE '%C4010%' OR modelo LIKE '%E57540%') 
                        AND (ciano <= 5 OR amarelo <= 5 OR magenta <= 5) 
                        AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                        ORDER BY data DESC, ip DESC''',
    'pesquisaFusor': '''SELECT ip, serial, modelo, local, data, fusor 
                        FROM INVENTARIO_TI_PRINTERS 
                        WHERE fusor IS NOT NULL 
                        AND fusor <= 15 
                        AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                        ORDER BY fusor DESC''',
    'pesquisaImagem': '''SELECT ip, serial, modelo, local, data, imagem 
                         FROM INVENTARIO_TI_PRINTERS 
                         WHERE imagem IS NOT NULL 
                         AND imagem <= 10 
                         AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                         ORDER BY imagem DESC''',
    'pesquisaBelt': '''SELECT ip, serial, modelo, local, data, belt 
                       FROM INVENTARIO_TI_PRINTERS 
                       WHERE belt IS NOT NULL 
                       AND belt <= 10 
                       AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                       ORDER BY belt DESC''',
    'pesquisaImpressorasUSB': '''SELECT serial, modelo, local 
                                FROM INVENTARIO_TI_PRINTERS 
                                WHERE ip IS NULL 
                                AND (local NOT LIKE '%BACKUP%') 
                                AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                                AND (tp_conexao = 'USB') 
                                ORDER BY local ASC''',
    'pesquisaImpressorasBackup': '''SELECT serial, modelo, local 
                                   FROM INVENTARIO_TI_PRINTERS 
                                   WHERE ip IS NULL 
                                   AND (local LIKE '%BACKUP%') 
                                   AND (modelo LIKE 'HP%' OR modelo LIKE 'SAMSUNG%') 
                                   AND (tp_conexao = 'USB') 
                                   ORDER BY local ASC''',
    'serieImpressoras': '''SELECT DISTINCT SERIAL 
                           FROM INVENTARIO_TI_PRINTERS 
                           WHERE MODELO LIKE '%HP%' OR MODELO LIKE 'SAMSUNG%' 
                           ORDER BY SERIAL ASC''',
    'modeloToners': '''SELECT MODELO 
                       FROM INVENTARIO_TI_TONERS_MODELOS 
                       ORDER BY MODELO ASC''',
    'statusToners': '''SELECT STATUS 
                       FROM INVENTARIO_TI_TONERS_STATUS 
                       ORDER BY STATUS ASC''',
    'somaEstoque': '''SELECT E.MODELO, E.QTD - S.QTD AS SALDO 
                      FROM INV_TI_VIEW_E_SOMA E 
                      LEFT JOIN INV_TI_VIEW_S_SOMA S 
                      ON S.MODELO = E.MODELO 
                      ORDER BY E.MODELO ASC''',
    'entradasToners': '''SELECT MODELO, QTD, DATA 
                         FROM INVENTARIO_TI_TONERS_ENTRADAS 
                         ORDER BY DATA DESC''',
    'saidasToners': '''SELECT MODELO, QTD, DATA, STATUS, SERIES, UPPER(SERIALTONER), UPPER(CHAMADO) 
                       FROM INVENTARIO_TI_TONERS_SAIDAS 
                       ORDER BY DATA DESC''',
}

INSERT_QUERIES = {
    'insertEntradasToners': '''INSERT INTO INVENTARIO_TI_TONERS_ENTRADAS (MODELO, QTD) VALUES (?, ?)''',
    'insertSaidasToners': '''INSERT INTO INVENTARIO_TI_TONERS_SAIDAS (MODELO, STATUS, SERIES, SERIALTONER, CHAMADO) VALUES (?, ?, ?, ?, ?)''',
}


def get_db_connection():
    """Estabelece a conexão com o banco de dados SQLite."""
    return sqlite3.connect(DATABASE)


def execute_query(query, params=None):
    """Executa uma consulta SQL e retorna os resultados."""
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        data = cursor.fetchall()
    return data


def xstr(s):
    return '' if s is None else str(s)


@app.route('/')
def raiz():
    return render_template('index.html')


@app.route('/parque_ativo')
def parque_ativo():
    data = execute_query(QUERIES['pesquisaFull'])
    data = [[xstr(value) for value in row] for row in data]
    return render_template('parque_ativo.html', data=data)


@app.route('/black')
def tpreto():
    data = execute_query(QUERIES['pesquisaK'])
    return render_template('black.html', dataP=data)


@app.route('/color')
def tcolor():
    data = execute_query(QUERIES['pesquisaColor'])
    return render_template('color.html', dataC=data)


@app.route('/fusor')
def fusor():
    data = execute_query(QUERIES['pesquisaFusor'])
    return render_template('fusor.html', dataF=data)


@app.route('/imagem')
def imagem():
    data = execute_query(QUERIES['pesquisaImagem'])
    return render_template('imagem.html', dataI=data)


@app.route('/belt')
def belt():
    data = execute_query(QUERIES['pesquisaBelt'])
    return render_template('belt.html', dataB=data)


@app.route('/usb')
def usb():
    data = execute_query(QUERIES['pesquisaImpressorasUSB'])
    return render_template('usb.html', dataIU=data)


@app.route('/backups')
def backups():
    data = execute_query(QUERIES['pesquisaImpressorasBackup'])
    return render_template('backups.html', dataIB=data)


@app.route('/saida', methods=['GET', 'POST'])
def saida():
    if request.method == "GET":
        series = execute_query(QUERIES['serieImpressoras'])
        equipamentos = execute_query(QUERIES['modeloToners'])
        status = execute_query(QUERIES['statusToners'])
        return render_template('saida.html', series=series, equipamentos=equipamentos, status=status)

    if request.method == "POST":
        dados = (
            request.form["equipamento_toner"],
            request.form["status_toner"],
            request.form["serie_equipamento"],
            request.form["serial_toner"],
            request.form["num_chamado"]
        )
        execute_query(INSERT_QUERIES['insertSaidasToners'], dados)
        return redirect(url_for('estoque'))


@app.route('/entrada', methods=['GET', 'POST'])
def entrada():
    if request.method == "GET":
        data = execute_query(QUERIES['modeloToners'])
        return render_template('entrada.html', data=data)

    if request.method == "POST":
        dados = (
            request.form["modelo_toner"],
            int(request.form["quantidade_toner"])
        )
        execute_query(INSERT_QUERIES['insertEntradasToners'], dados)
        return redirect(url_for('estoque'))


@app.route('/estoque')
def estoque():
    data = execute_query(QUERIES['somaEstoque'])
    return render_template('estoque.html', data=data)


@app.route('/entradas_toners')
def entradas_toners():
    data = execute_query(QUERIES['entradasToners'])
    return render_template('entradas_toners.html', data=data)


@app.route('/saidas_toners')
def saidas_toners():
    data = execute_query(QUERIES['saidasToners'])
    return render_template('saidas_toners.html', data=data)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
