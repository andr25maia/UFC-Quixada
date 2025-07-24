import os
from dotenv import load_dotenv

import pandas as pd
import psycopg2 as pg
import sqlalchemy
from sqlalchemy import create_engine
import panel as pn

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

con = pg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

cnx = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
sqlalchemy.create_engine(cnx)

query = "select * from public.denuncia;" 
df = pd.read_sql_query(query, cnx)

df

pn.extension()
pn.extension('tabulator')
pn.extension(notifications=True)

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

flag=''

descricao = pn.widgets.TextInput(
    name = "Descrição",
    value='',
    placeholder='Digite uma descrição para a denúncia',
    disabled=False
)

observacoes = pn.widgets.TextInput(
    name="Observações",
    value='',
    placeholder='Digite observações adicionais',
    disabled=False
)

data_registro = pn.widgets.DatePicker(
    name="Data de Registro",
    disabled=False
)

CPF_assistente = pn.widgets.TextInput(
    name="CPF do Assistente Social",
    value='',
    placeholder='Digite o CPF do assistente social',
    disabled=False
)

cod_familia = pn.widgets.TextInput(
    name="Código da Família",
    value='',
    placeholder='Digite o código da família',
    disabled=False
)

status = pn.widgets.Select(
    name="Status",
    options=['', 'Aberta', 'Em processo', 'Resolvida'],
    value='',
    disabled=False
)

id_denuncia = pn.widgets.TextInput(
    name="ID da Denúncia",
    value='',
    placeholder='Digite o ID da denúncia',
    disabled=False
)

buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

output = pn.Column()

status_map = {
    'Aberta': 0,
    'Em processo': 1,
    'Resolvida': 2
}

btn_limpar_data = pn.widgets.Button(name="Limpar Data")

def limpar_data(event):
    data_registro.value = None

btn_limpar_data.on_click(limpar_data)



def queryAll():
    query = f"select * from public.denuncia"
    df = pd.read_sql_query(query, cnx)
    
    # Mapear os valores numéricos do status para texto legível
    reverse_status_map = {0: 'Aberta', 1: 'Em processo', 2: 'Resolvida'}
    if 'status' in df.columns:
        df['status'] = df['status'].map(reverse_status_map)
    
    # Reordenar colunas para uma visualização mais intuitiva
    if not df.empty:
        # Define a ordem desejada das colunas
        colunas_ordenadas = ['id_denuncia', 'descricao', 'observacoes', 'data_registro', 'status', 'cod_familia', 'cpf_assistente']
        # Filtra apenas as colunas que existem no DataFrame
        colunas_existentes = [col for col in colunas_ordenadas if col in df.columns]
        # Adiciona qualquer coluna que não esteja na lista ordenada
        colunas_restantes = [col for col in df.columns if col not in colunas_existentes]
        colunas_finais = colunas_existentes + colunas_restantes
        df = df[colunas_finais]
    
    return pn.widgets.Tabulator(df, height=400, sizing_mode='stretch_width', pagination='remote', page_size=10)

output.append(queryAll())

def on_consultar(event):
    filtros = []
    valores = []

    if descricao.value:
        filtros.append("descricao ILIKE %s")
        valores.append(f"%{descricao.value}%")

    if observacoes.value:
        filtros.append("observacoes ILIKE %s")
        valores.append(f"%{observacoes.value}%")

    if data_registro.value:
        filtros.append("data_registro = %s")
        valores.append(data_registro.value.strftime('%Y-%m-%d'))

    if CPF_assistente.value:
        filtros.append("cpf_assistente = %s")
        valores.append(CPF_assistente.value)

    if cod_familia.value:
        filtros.append("cod_familia = %s")
        valores.append(cod_familia.value)

    if status.value:
        filtros.append("status = %s")
        valores.append(status_map[status.value])

    if id_denuncia.value:
        if id_denuncia.value.isdigit():
            filtros.append("id_denuncia = %s")
            valores.append(int(id_denuncia.value))
        else:
            pn.state.notifications.error("ID da denúncia deve ser um número inteiro.")
            return

    if not filtros:
        pn.state.notifications.error("Informe ao menos um campo para consultar.")
        return

    query = "SELECT * FROM public.denuncia WHERE " + " AND ".join(filtros)

    try:
        df = pd.read_sql(query, con=con, params=tuple(valores))
        output.clear()
        if df.empty:
            pn.state.notifications.warning("Nenhum registro encontrado. Exibindo todos.")
            output.append(queryAll())
        else:
            # Mapear os valores numéricos do status para texto legível
            reverse_status_map = {0: 'Aberta', 1: 'Em processo', 2: 'Resolvida'}
            if 'status' in df.columns:
                df['status'] = df['status'].map(reverse_status_map)
            
            # Reordenar colunas para uma visualização mais intuitiva
            if not df.empty:
                colunas_ordenadas = ['id_denuncia', 'descricao', 'observacoes', 'data_registro', 'status', 'cod_familia', 'cpf_assistente']
                colunas_existentes = [col for col in colunas_ordenadas if col in df.columns]
                colunas_restantes = [col for col in df.columns if col not in colunas_existentes]
                colunas_finais = colunas_existentes + colunas_restantes
                df = df[colunas_finais]
            
            btn_voltar = pn.widgets.Button(name="<< Voltar", button_type="primary")

            def voltar(event):
                output.clear()
                output.append(queryAll())

            btn_voltar.on_click(voltar)
            output.append(pn.Column(btn_voltar, pn.widgets.Tabulator(df, height=300, sizing_mode='stretch_width')))
    except Exception as e:
        pn.state.notifications.error(f"Erro ao consultar: {e}")

def on_inserir(event=None):
    try:
        cursor = con.cursor()
        status_num = status_map[status.value] 
        cursor.execute(
            "INSERT INTO public.denuncia (descricao, observacoes, data_registro, cpf_assistente, cod_familia, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (descricao.value, observacoes.value, data_registro.value, CPF_assistente.value, cod_familia.value, status_num)
        )
        con.commit()
        cursor.close()

        # Limpa os campos do formulário
        descricao.value = ''
        observacoes.value = ''
        data_registro.value = None
        CPF_assistente.value = ''
        cod_familia.value = ''
        status.value = 'Aberta'
        id_denuncia.value = ''

        output.clear()
        output.append(queryAll())
        pn.state.notifications.success("Denúncia inserida com sucesso.")
    except Exception as e:
        con.rollback()
        if cursor:
            cursor.close()
        pn.state.notifications.error(f"Erro ao inserir: {e}")

def on_atualizar(event=None):
    try:
        if not id_denuncia.value or not id_denuncia.value.isdigit():
            pn.state.notifications.error("ID da denúncia deve ser um número válido.")
            return

        campos = []
        valores = []

        if descricao.value:
            campos.append("descricao = %s")
            valores.append(descricao.value)

        if observacoes.value:
            campos.append("observacoes = %s")
            valores.append(observacoes.value)

        if data_registro.value:
            campos.append("data_registro = %s")
            valores.append(data_registro.value)

        if CPF_assistente.value:
            campos.append("cpf_assistente = %s")
            valores.append(CPF_assistente.value)

        if cod_familia.value:
            campos.append("cod_familia = %s")
            valores.append(cod_familia.value)

        if status.value:
            status_num = status_map[status.value]
            campos.append("status = %s")
            valores.append(status_num)

        if not campos:
            pn.state.notifications.warning("Preencha ao menos um campo para atualizar.")
            return

        valores.append(int(id_denuncia.value))

        query = f"UPDATE public.denuncia SET {', '.join(campos)} WHERE id_denuncia = %s"

        cursor = con.cursor()
        cursor.execute(query, tuple(valores))
        con.commit()
        cursor.close()

        output.clear()
        output.append(queryAll())
        pn.state.notifications.success("Denúncia atualizada com sucesso.")
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f"Erro ao atualizar: {e}")


def on_excluir(event=None):
    try:
        if not id_denuncia.value or not id_denuncia.value.isdigit():
            pn.state.notifications.error("ID da denúncia deve ser um número válido.")
            return

        cursor = con.cursor()
        cursor.execute("DELETE FROM public.denuncia WHERE id_denuncia=%s", (int(id_denuncia.value),))
        con.commit()
        cursor.close()
        output.clear()
        output.append(queryAll())
        pn.state.notifications.success("Denúncia excluída com sucesso.")
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f"Erro ao excluir: {e}")

# Conecta botões às funções
buttonConsultar.on_click(on_consultar)
buttonInserir.on_click(on_inserir)
buttonAtualizar.on_click(on_atualizar)
buttonExcluir.on_click(on_excluir)

# Interface
pn.Row(
    pn.Column(
        "## Denúncia - CRUD",
        id_denuncia,
        descricao, 
        observacoes,
        pn.Column(
            data_registro,
            btn_limpar_data
        ),
        status,
        cod_familia,
        CPF_assistente,
        pn.Row(buttonConsultar, buttonInserir, buttonAtualizar, buttonExcluir)
    ),
    pn.Column(output)
).servable()