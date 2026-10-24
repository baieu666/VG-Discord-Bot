import sqlite3
from contextlib import closing
from pathlib import Path


ARQUIVO_BLOQUEIOS = (
    Path(__file__).resolve().parent.parent / 'bloqueios.sqlite3'
)


def banco_bloqueios(sql, parametros=()):
    with closing(sqlite3.connect(ARQUIVO_BLOQUEIOS)) as conexao:
        resultado = conexao.execute(sql, parametros).fetchone()
        conexao.commit()
        return resultado


banco_bloqueios("""
    CREATE TABLE IF NOT EXISTS bloqueios (
        canal_id INTEGER PRIMARY KEY,
        envio_original INTEGER
    )
""")

