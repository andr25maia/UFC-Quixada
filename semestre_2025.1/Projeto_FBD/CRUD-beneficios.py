import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2 as pg
import sqlalchemy
from sqlalchemy import create_engine, text
import panel as pn
from datetime import date

# Carrega variáveis de ambiente do arquivo .env (opcional, mas boa prática)
load_dotenv()

# --- Configuração da Conexão com o Banco de Dados ---
# Substitua com suas credenciais ou certifique-se que o .env está configurado
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'seu_banco')
DB_USER = os.getenv('DB_USER', 'seu_usuario')
DB_PASS = os.getenv('DB_PASS', 'sua_senha')

# Conexão usando psycopg2 (para executar comandos como INSERT, UPDATE, DELETE)
try:
    con = pg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
except pg.OperationalError as e:
    print(f"Erro ao conectar com psycopg2: {e}")
    con = None

# Conexão usando SQLAlchemy (para ler dados com Pandas)
try:
    cnx_str = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
    engine = sqlalchemy.create_engine(cnx_str)
except Exception as e:
    print(f"Erro ao conectar com SQLAlchemy: {e}")
    engine = None

# --- Interface Gráfica com Panel ---
pn.extension('tabulator', notifications=True)

# --- Widgets para os campos da tabela 'beneficio' ---
# Agora, estes widgets são usados tanto para entrada de dados quanto para filtros de consulta
cod_beneficio_input = pn.widgets.TextInput(
    name="Código do Benefício",
    placeholder='Filtrar por código exato',
    value=''
)

nome_input = pn.widgets.TextInput(
    name="Nome do Benefício",
    placeholder='Filtrar por parte do nome',
    value=''
)

valor_input = pn.widgets.IntInput(
    name="Valor (R$)",
    value=0, # 0 será ignorado no filtro
    step=10
)

data_inicio_input = pn.widgets.DatePicker(
    name='Data de Início',
    value=None # Nulo por padrão
)

data_fim_input = pn.widgets.DatePicker(
    name='Data de Fim',
    value=None # Nulo por padrão
)

# --- Botões de Ação ---
buttonConsultar = pn.widgets.Button(name='Consultar / Filtrar', button_type='primary')
buttonLimpar = pn.widgets.Button(name='Limpar Filtros', button_type='default')
buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

def queryAll():
    """Função para buscar e exibir todos os benefícios em uma tabela."""
    if engine is None:
        return pn.pane.Alert('Conexão com o banco de dados não estabelecida.', alert_type='danger')
    try:
        query = "SELECT * FROM public.beneficio ORDER BY cod_beneficio;"
        df = pd.read_sql_query(query, engine)
        return pn.widgets.Tabulator(df, layout='fit_data', page_size=10, disabled=True)
    except Exception as e:
        pn.state.notifications.error(f'Erro ao carregar dados: {e}')
        return pn.pane.Alert(f'Não foi possível consultar a tabela de benefícios: {e}', alert_type='danger')

def on_consultar(event):
    """Função para consultar benefícios com base em múltiplos campos de filtro, incluindo renda."""
    if engine is None:
        pn.state.notifications.error('Conexão com o banco de dados não estabelecida.')
        return
    try:
        base_query = "SELECT * FROM public.beneficio"
        conditions = []
        params = {}

        if cod_beneficio_input.value:
            conditions.append("cod_beneficio = :cod")
            params['cod'] = int(cod_beneficio_input.value)

        if nome_input.value:
            conditions.append("nome ILIKE :nome")
            params['nome'] = f"%{nome_input.value}%"

        if valor_input.value is not None and valor_input.value > 0:
            conditions.append("valor = :valor")
            params['valor'] = valor_input.value

        if data_inicio_input.value:
            conditions.append("data_inicio = :d_inicio")
            params['d_inicio'] = data_inicio_input.value

        if data_fim_input.value:
            conditions.append("data_fim = :d_fim")
            params['d_fim'] = data_fim_input.value

        # Filtro por renda (se existir o campo 'renda' na tabela)
        # Adicione um widget para renda se ainda não existir:
        # renda_input = pn.widgets.IntInput(name="Renda", value=0, step=10)
        # E inclua no layout e nos filtros:
        # if renda_input.value is not None and renda_input.value > 0:
        #     conditions.append("renda = :renda")
        #     params['renda'] = renda_input.value

        if not conditions:
            query = f"{base_query} ORDER BY cod_beneficio;"
        else:
            query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY cod_beneficio;"
        
        df = pd.read_sql_query(sql=text(query), con=engine, params=params)

        if df.empty:
            pn.state.notifications.warning('Nenhum benefício encontrado com os critérios informados.')
        
        interactive_table[0] = pn.widgets.Tabulator(df, layout='fit_data', page_size=10, disabled=True)

    except ValueError:
        pn.state.notifications.error('O Código do Benefício e o Valor devem ser números válidos.')
    except Exception as e:
        pn.state.notifications.error(f'Erro na consulta: {e}')

def on_inserir(event):
    """Função para inserir um novo benefício."""
    if con is None:
        pn.state.notifications.error('Conexão com o banco de dados não estabelecida.')
        return
    
    if not nome_input.value or valor_input.value <= 0 or not data_inicio_input.value:
        pn.state.notifications.error('Nome, Valor (>0) e Data de Início são obrigatórios para inserir!')
        return

    try:
        cursor = con.cursor()
        query = "INSERT INTO public.beneficio (nome, valor, data_inicio, data_fim) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nome_input.value, valor_input.value, data_inicio_input.value, data_fim_input.value))
        con.commit()
        cursor.close()
        pn.state.notifications.success('Benefício inserido com sucesso!')
        on_limpar(None) 
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Não foi possível inserir: {e}')

def on_atualizar(event):
    """Função para atualizar um benefício existente, mantendo valores antigos se campos estiverem nulos/vazios."""
    if con is None:
        pn.state.notifications.error('Conexão com o banco de dados não estabelecida.')
        return

    if not cod_beneficio_input.value:
        pn.state.notifications.error('É necessário informar o Código do Benefício para atualizar.')
        return

    try:
        cursor = con.cursor()
        # Busca os valores atuais do registro
        cursor.execute(
            "SELECT nome, valor, data_inicio, data_fim FROM public.beneficio WHERE cod_beneficio = %s",
            (int(cod_beneficio_input.value),)
        )
        row = cursor.fetchone()
        if not row:
            pn.state.notifications.warning('Nenhum benefício encontrado com o código informado para atualizar.')
            cursor.close()
            return

        nome_antigo, valor_antigo, data_inicio_antiga, data_fim_antiga = row

        # Usa o valor do input se fornecido, senão mantém o antigo
        nome_novo = nome_input.value if nome_input.value else nome_antigo
        valor_novo = valor_input.value if valor_input.value and valor_input.value > 0 else valor_antigo
        data_inicio_nova = data_inicio_input.value if data_inicio_input.value else data_inicio_antiga
        data_fim_nova = data_fim_input.value if data_fim_input.value else data_fim_antiga

        query = """
            UPDATE public.beneficio
            SET nome = %s, valor = %s, data_inicio = %s, data_fim = %s
            WHERE cod_beneficio = %s
        """
        cursor.execute(query, (nome_novo, valor_novo, data_inicio_nova, data_fim_nova, int(cod_beneficio_input.value)))
        con.commit()
        
        if cursor.rowcount == 0:
            pn.state.notifications.warning('Nenhum benefício encontrado com o código informado para atualizar.')
        else:
            pn.state.notifications.success('Benefício atualizado com sucesso!')
        
        cursor.close()
        on_limpar(None)
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Não foi possível atualizar: {e}')

def on_excluir(event):
    if con is None:
        pn.state.notifications.error('Conexão com o banco de dados não estabelecida.')
        return

    if not cod_beneficio_input.value:
        pn.state.notifications.error('É necessário informar o Código do Benefício para excluir.')
        return

    try:
        cursor = con.cursor()
        # Exclui o benefício normalmente
        query = "DELETE FROM public.beneficio WHERE cod_beneficio = %s"
        cursor.execute(query, (int(cod_beneficio_input.value),))
        con.commit()

        if cursor.rowcount == 0:
            pn.state.notifications.warning('Nenhum benefício encontrado com o código informado para excluir.')
        else:
            # Após excluir, faz o TRUNCATE se a tabela ficou vazia
            cursor.execute("SELECT COUNT(*) FROM public.beneficio")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("TRUNCATE TABLE public.beneficio RESTART IDENTITY CASCADE;")
                con.commit()
            pn.state.notifications.success('Benefício excluído com sucesso!')

        cursor.close()
        on_limpar(None)
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Não foi possível excluir. Verifique se este benefício está sendo usado em outras tabelas (ex: \"recebe\"). Erro: {e}')

def on_limpar(event):
    """Limpa todos os campos de filtro e recarrega a tabela completa."""
    cod_beneficio_input.value = ''
    nome_input.value = ''
    valor_input.value = 0
    data_inicio_input.value = None
    data_fim_input.value = None
    interactive_table[0] = queryAll()

buttonConsultar.on_click(on_consultar)
buttonInserir.on_click(on_inserir)
buttonAtualizar.on_click(on_atualizar)
buttonExcluir.on_click(on_excluir)
buttonLimpar.on_click(on_limpar)

interactive_table = pn.Column(queryAll())

app_layout = pn.Row(
    pn.Column(
        '### **Gerenciamento de Benefícios**',
        pn.layout.Divider(),
        '**Filtros de Consulta / Dados para Ações**',
        cod_beneficio_input,
        nome_input,
        valor_input,
        data_inicio_input,
        data_fim_input,
        pn.layout.Divider(),
        '**Ações**',
        pn.Row(buttonConsultar, buttonLimpar),
        pn.Row(buttonInserir, buttonAtualizar, buttonExcluir)
    ),
    pn.Column(
        '### **Benefícios Cadastrados**',
        interactive_table,
        width=800
    )
)

app_layout.servable()
