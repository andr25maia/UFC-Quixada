import os
from dotenv import load_dotenv

import pandas as pd
from sqlalchemy import create_engine
import psycopg2 as pg
import panel as pn

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

con = pg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
cnx = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = create_engine(cnx)

pn.extension('tabulator', notifications=True)

# CSS personalizado
custom_css = """
.bk-btn-primary { background-color: #85b8ff !important; border: 1.5px solid rgba(51, 102, 204, 0.4) !important; color: white !important; font-weight: 600; border-radius: 8px; box-shadow: 0 2px 5px rgba(51, 102, 204, 0.2); transition: background-color 0.3s ease, box-shadow 0.3s ease; }
.bk-btn-primary:hover { background-color: #5590ff !important; box-shadow: 0 4px 8px rgba(51, 102, 204, 0.35); }

.bk-btn-success { background-color: #7dd77d !important; border: 1.5px solid rgba(47, 158, 68, 0.4) !important; color: white !important; font-weight: 600; border-radius: 8px; box-shadow: 0 2px 5px rgba(47, 158, 68, 0.2); transition: background-color 0.3s ease, box-shadow 0.3s ease; }
.bk-btn-success:hover { background-color: #4fae46 !important; box-shadow: 0 4px 8px rgba(47, 158, 68, 0.35); }

.bk-btn-warning { background-color: #ffe066 !important; border: 1.5px solid rgba(224, 168, 0, 0.3) !important; color: white !important; font-weight: 600; border-radius: 8px; box-shadow: 0 2px 5px rgba(224, 168, 0, 0.2); transition: background-color 0.3s ease, box-shadow 0.3s ease; }
.bk-btn-warning:hover { background-color: #d4b000 !important; box-shadow: 0 4px 8px rgba(224, 168, 0, 0.35); }

.bk-btn-danger { background-color: #f17c8e !important; border: 1.5px solid rgba(200, 35, 51, 0.3) !important; color: white !important; font-weight: 600; border-radius: 8px; box-shadow: 0 2px 5px rgba(200, 35, 51, 0.2); transition: background-color 0.3s ease, box-shadow 0.3s ease; }
.bk-btn-danger:hover { background-color: #c64556 !important; box-shadow: 0 4px 8px rgba(200, 35, 51, 0.35); }
"""

pn.config.raw_css.append(custom_css)

pnome = pn.widgets.TextInput(name="Primeiro Nome", placeholder="Digite o primeiro nome")
sobrenome = pn.widgets.TextInput(name="Sobrenome", placeholder="Digite o sobrenome")
cpf = pn.widgets.TextInput(name="CPF", placeholder="Digite o CPF")
senha = pn.widgets.PasswordInput(name="Senha", placeholder="Digite a senha")

buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary', sizing_mode='stretch_width')
buttonInserir = pn.widgets.Button(name='Inserir', button_type='success', sizing_mode='stretch_width')
buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning', sizing_mode='stretch_width')
buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger', sizing_mode='stretch_width')

output = pn.Column()

def limpar_campos():
    pnome.value = ''
    sobrenome.value = ''
    cpf.value = ''
    senha.value = ''

def validar_campos(required=True):
    if required and not all([pnome.value, sobrenome.value, cpf.value, senha.value]):
        pn.state.notifications.error("Por favor, preencha todos os campos.")
        return False
    if not cpf.value:
        pn.state.notifications.error("CPF é obrigatório para esta operação.")
        return False
    return True

def query_all():
    df = pd.read_sql("SELECT * FROM public.assistente_social", engine)
    return pn.widgets.Tabulator(df, height=400, sizing_mode='stretch_width', pagination='remote', page_size=10)

def on_consultar(event):
    filtros = []
    valores = []

    if pnome.value:
        filtros.append("pnome ILIKE %s")
        valores.append(f"%{pnome.value}%")
    if sobrenome.value:
        filtros.append("sobrenome ILIKE %s")
        valores.append(f"%{sobrenome.value}%")
    if cpf.value:
        filtros.append("cpf = %s")
        valores.append(cpf.value)
    if senha.value:
        filtros.append("senha = %s")
        valores.append(senha.value)

    if not filtros:
        pn.state.notifications.error("Informe ao menos um campo para consultar.")
        return

    query = "SELECT * FROM public.assistente_social WHERE " + " AND ".join(filtros)

    try:
        df = pd.read_sql(query, engine, params=tuple(valores)) 
        output.clear()
        if df.empty:
            pn.state.notifications.warning("Nenhum registro encontrado. Exibindo todos os registros.")
            output.append(query_all())
        else:
            def voltar_tabela(event):
                output.clear()
                output.append(query_all())

            btn_voltar = pn.widgets.Button(name="<< Voltar para tabela completa", button_type="primary")
            btn_voltar.on_click(voltar_tabela)

            output.append(pn.Column(
                btn_voltar,
                pn.widgets.Tabulator(df, height=300, sizing_mode='stretch_width')
            ))
    except Exception as e:
        pn.state.notifications.error(f"Erro ao consultar: {e}")

def on_inserir(event):
    if not validar_campos():
        return
    try:
        with con.cursor() as cursor:
            cursor.execute(
                "INSERT INTO public.assistente_social (pnome, sobrenome, cpf, senha) VALUES (%s, %s, %s, %s)",
                (pnome.value, sobrenome.value, cpf.value, senha.value)
            )
            con.commit()
        pn.state.notifications.success("Registro inserido com sucesso!")
        limpar_campos()
        output.clear()
        output.append(query_all())
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f"Erro ao inserir: {e}")

def on_atualizar(event):
    if not cpf.value:
        pn.state.notifications.error("Informe o CPF para atualização.")
        return
    try:
        df = pd.read_sql(
            "SELECT pnome, sobrenome, senha FROM public.assistente_social WHERE cpf = %s",
            engine,
            params=(cpf.value,)
        )
        if df.empty:
            pn.state.notifications.warning("Nenhum registro encontrado para atualização.")
            return
        
        atual = df.iloc[0]
        
        pnome_novo = pnome.value if pnome.value else atual['pnome']
        sobrenome_novo = sobrenome.value if sobrenome.value else atual['sobrenome']
        senha_nova = senha.value if senha.value else atual['senha']
        
        with con.cursor() as cursor:
            cursor.execute(
                "UPDATE public.assistente_social SET pnome = %s, sobrenome = %s, senha = %s WHERE cpf = %s",
                (pnome_novo, sobrenome_novo, senha_nova, cpf.value)
            )
            con.commit()
        pn.state.notifications.success("Registro atualizado com sucesso!")
        limpar_campos()
        output.clear()
        output.append(query_all())
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f"Erro ao atualizar: {e}")

def on_excluir(event):
    if not cpf.value:
        pn.state.notifications.error("Informe o CPF para exclusão.")
        return
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM public.assistente_social WHERE cpf = %s", (cpf.value,))
            deleted = cursor.rowcount
            con.commit()
        if deleted:
            pn.state.notifications.success("Registro excluído com sucesso!")
        else:
            pn.state.notifications.warning("Nenhum registro encontrado para exclusão.")
        limpar_campos()
        output.clear()
        output.append(query_all())
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f"Erro ao excluir: {e}")

buttonConsultar.on_click(on_consultar)
buttonInserir.on_click(on_inserir)
buttonAtualizar.on_click(on_atualizar)
buttonExcluir.on_click(on_excluir)

inputs = pn.Column(
    pn.pane.Markdown("## Assistente Social CRUD"),
    pnome, sobrenome, cpf, senha,
    pn.Row(buttonConsultar, buttonInserir, buttonAtualizar, buttonExcluir, sizing_mode='stretch_width'),
    sizing_mode='fixed',
    width=400,
    margin=(10, 20)
)

output.append(query_all())
dashboard = pn.Row(inputs, output, sizing_mode='stretch_both')

dashboard.servable()
