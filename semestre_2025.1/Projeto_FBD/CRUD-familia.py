import os
from dotenv import load_dotenv

import requests
import pandas as pd
import psycopg2 as pg
import sqlalchemy
from sqlalchemy import create_engine
import panel as pn

# Configurando o BD

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

con = pg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
cnx = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = create_engine(cnx)

pn.extension('tabulator', notifications=True)

# Inputs
nis_responsavel = pn.widgets.TextInput(
    name="Nis responsável",
    placeholder='Insira o nis do responsável'
)

renda_per_capita = pn.widgets.TextInput(
    name="Renda per capita",
    placeholder='Insira a renda per capta da família'
)

pontuacao_vulnerabilidade = pn.widgets.TextInput(
    name="Pontuação de vulnerabilidade",
    placeholder='Insira a pontuação de vulnerabilidade da família'
)

cep = pn.widgets.TextInput(
    name="CEP",
    placeholder="Digite o CEP da família",
    disabled=False
)
estado = pn.widgets.TextInput(
    name="Estado",
    disabled=True
)
cidade = pn.widgets.TextInput(
    name="Cidade",
    disabled=True
)
regiao = pn.widgets.TextInput(
    name="Região"
)
rua = pn.widgets.TextInput(
    name="Rua",
    disabled=True
)
bairro = pn.widgets.TextInput(
    name="Bairro",
    disabled=True
)
numero = pn.widgets.TextInput(
    name="Número"
)

def validar_campos(required=True):
    if required and not all([nis_responsavel.value, renda_per_capita.value, pontuacao_vulnerabilidade.value, cep.value, estado.value, cidade.value, regiao.value, rua.value, bairro.value, numero.value]):
        pn.state.notifications.error("Por favor, preencha todos os campos.")
        return False
    return True

output = pn.Column()

def limpar_campos():
    renda_per_capita.value = ''
    pontuacao_vulnerabilidade.value = ''
    cep.value = ''
    estado.value = ''
    cidade.value = ''
    regiao.value = ''
    rua.value = ''
    bairro.value = ''
    numero.value = ''
    nis_responsavel.value = ''

cep_tratado = ''

def buscar_dados_cep(event):
    cep_tratado = cep.value.strip().replace("-", "")
    print("Função chamada busca_dados_cep")
    if len(cep_tratado) != 8 or not cep_tratado.isdigit():
        return

    url = f"https://brasilapi.com.br/api/cep/v1/{cep_tratado}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        estado.value = data.get("state", "")
        cidade.value = data.get("city", "")
        bairro.value = data.get("neighborhood", "")
        rua.value = data.get("street", "")
        
cep.param.watch(buscar_dados_cep, "value")

#Botões
buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary', sizing_mode='stretch_width')
buttonInserir = pn.widgets.Button(name='Inserir', button_type='success', sizing_mode='stretch_width')
buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning', sizing_mode='stretch_width')
buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger', sizing_mode='stretch_width')

# Consulta geral:
def query_all():
    df = pd.read_sql("SELECT * FROM public.familia", engine)
    return pn.widgets.Tabulator(df, height=400, sizing_mode='stretch_width', pagination='remote', page_size=10)

#Consulta:
def on_consultar(event):
    filtros = []
    valores = []
    cep_tratado = cep.value.strip().replace("-", "")
    
    if estado.value:
        filtros.append("estado ILIKE %s")
        valores.append(f"%{estado.value}%")
    if cidade.value:
        filtros.append("cidade ILIKE %s")
        valores.append(f"%{cidade.value}%")
    if regiao.value:
        filtros.append("regiao ILIKE %s")
        valores.append(f"%{regiao.value}")
    if cep_tratado:
        filtros.append("cep = %s")
        valores.append(int(cep_tratado))
    if pontuacao_vulnerabilidade.value:
        filtros.append("pontuacao_vulnerabilidade = %s")
        valores.append(int(pontuacao_vulnerabilidade.value))
    if renda_per_capita.value:
        filtros.append("renda_per_capita = %s")
        valores.append(int(renda_per_capita.value))
    if nis_responsavel.value:
        filtros.append("nis_responsavel = %s")
        valores.append(nis_responsavel.value)

    if not filtros:
        pn.state.notifications.error("Informe ao menos um campo para consultar.")
        return

    query = "SELECT * FROM public.familia WHERE " + " AND ".join(filtros)

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
        print(e)

# Inserir
def on_inserir(event):
    if not validar_campos():
        return
    try:
        cep_tratado = cep.value.strip().replace("-", "")
        with con.cursor() as cursor:
            cursor.execute(
                "INSERT INTO public.familia (estado,cidade,regiao, CEP, rua, numero, pontuacao_vulnerabilidade, renda_per_capita, bairro, nis_responsavel) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)", 
                (estado.value,cidade.value,regiao.value, int(cep_tratado), rua.value, numero.value, pontuacao_vulnerabilidade.value, int(renda_per_capita.value), bairro.value, nis_responsavel.value)
            )
            con.commit()
        pn.state.notifications.success("Registro inserido com sucesso!")
        limpar_campos()
        output.clear()
        output.append(query_all())
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f"Erro ao inserir: {e}")
        print(e)
    
# Put
def on_atualizar(event):
    if not nis_responsavel.value:
        pn.state.notifications.error("Informe o nis responsável para atualização.")
        return
    try:
        df = pd.read_sql(
            "SELECT estado,cidade,regiao, CEP, rua, numero, pontuacao_vulnerabilidade, renda_per_capita, bairro FROM public.familia WHERE nis_responsavel = %s",
            engine,
            params=(nis_responsavel.value,)
        )
        if df.empty:
            pn.state.notifications.warning("Nenhum registro encontrado para atualização.")
            return
        
        atual = df.iloc[0]
        cep_tratado = cep.value.strip().replace("-", "")
        estado_novo = estado.value if estado.value else atual['estado']
        cidade_novo = cidade.value if cidade.value else atual['cidade']
        regiao_nova = regiao.value if regiao.value else atual['regiao']
        cep_nova = cep_tratado if cep.value else float(atual['cep'])
        rua_nova = rua.value if rua.value else atual['rua']
        numero_nova = numero.value if numero.value else float(atual['numero'])
        pontuacao_vulnerabilidade_nova = pontuacao_vulnerabilidade.value if pontuacao_vulnerabilidade.value else atual['pontuacao_vulnerabilidade']
        renda_per_capita_nova = renda_per_capita.value if renda_per_capita.value else atual['renda_per_capita']
        bairro_nova = bairro.value if bairro.value else atual['bairro']
        
        with con.cursor() as cursor:
            cursor.execute(
                "UPDATE public.familia SET estado = %s, cidade = %s, regiao = %s, cep = %s, rua = %s, numero = %s, pontuacao_vulnerabilidade = %s, renda_per_capita = %s, bairro = %s WHERE nis_responsavel = %s",
                (estado_novo, cidade_novo, regiao_nova, cep_nova, rua_nova, numero_nova, int(pontuacao_vulnerabilidade_nova), renda_per_capita_nova, bairro_nova, nis_responsavel.value)
            )
            con.commit()
        pn.state.notifications.success("Registro atualizado com sucesso!")
        limpar_campos()
        output.clear()
        output.append(query_all())
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f"Erro ao atualizar: {e}")
        print(e)

# Delete
def on_excluir(event):
    if not nis_responsavel.value:
        pn.state.notifications.error("Informe o nis responsável para exclusão.")
        return
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM public.familia WHERE nis_responsavel = %s", (nis_responsavel.value,))
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


# Layout
buttonConsultar.on_click(on_consultar)
buttonInserir.on_click(on_inserir)
buttonAtualizar.on_click(on_atualizar)
buttonExcluir.on_click(on_excluir)

inputs = pn.Column(
    pn.pane.Markdown("## Família CRUD"),
    estado,cidade,regiao, cep, rua, numero, pontuacao_vulnerabilidade, renda_per_capita, bairro, nis_responsavel,
    pn.Row(buttonConsultar, buttonInserir, buttonAtualizar, buttonExcluir, sizing_mode='stretch_width'),
    sizing_mode='fixed',
    width=400,
    margin=(10, 20)
)

output.append(query_all())
dashboard = pn.Row(inputs, output, sizing_mode='stretch_both')

dashboard.servable()