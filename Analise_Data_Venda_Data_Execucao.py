import streamlit as st
import pandas as pd
import mysql.connector
import decimal

def gerar_df_sales():

    def gerar_df_phoenix(vw_name, base_luck):

        config = {
        'user': 'user_automation_jpa',
        'password': 'luck_jpa_2024',
        'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
        'database': base_luck
        }
        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()

        request_name = f'SELECT * FROM {vw_name}'
            
        cursor.execute(request_name)
        resultado = cursor.fetchall()
        cabecalho = [desc[0] for desc in cursor.description]
        cursor.close()
        conexao.close()
        df = pd.DataFrame(resultado, columns=cabecalho)
        df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
        return df

    st.session_state.df_sales = gerar_df_phoenix(
        'vw_tempo_data_venda_execucao', 
        'test_phoenix_recife'
    )

    st.session_state.df_sales['Setor'] = st.session_state.df_sales['Setor'].fillna('')

    st.session_state.df_sales['Canal_de_Vendas'] = st.session_state.df_sales['Canal_de_Vendas'].fillna('')

    st.session_state.df_sales['Data_Venda'] = pd.to_datetime(
        st.session_state.df_sales['Data_Venda']
    ).dt.date

def colher_filtros_escolhidos(row_filtros, row_periodo):

    with row_filtros[0]:

        filtrar_base_luck = st.multiselect(
            'Base Luck',
            sorted(st.session_state.df_sales['Base_Luck'].unique()),
            default=None
        )

    with row_filtros[1]:

        filtrar_setor = st.multiselect(
            'Setor',
            sorted(st.session_state.df_sales['Setor'].unique()),
            default=None
        )

    with row_filtros[2]:

        filtrar_canal_de_vendas = st.multiselect(
            'Canal de Vendas',
            sorted(st.session_state.df_sales['Canal_de_Vendas'].unique()),
            default=None
        )

    with row_periodo[0]:

        data_inicio = st.date_input(
            'Data (Venda) Início', 
            value=None, 
            format='DD/MM/YYYY'
        )

    with row_periodo[1]:

        data_fim = st.date_input(
            'Data (Venda) Fim', 
            value=None, 
            format='DD/MM/YYYY'
        )

    return filtrar_base_luck, filtrar_setor, filtrar_canal_de_vendas, data_inicio, data_fim

def aplicar_filtros_escolhidos():

    def filtrar_df(df, coluna_filtro, info_filtro):

        if len(info_filtro) > 0:

            df = df[
                df[coluna_filtro].isin(info_filtro)
            ]

        return df
    
    df_sales = st.session_state.df_sales.copy()

    df_sales = filtrar_df(
        df_sales, 
        'Base_Luck', 
        filtrar_base_luck
    )

    df_sales = filtrar_df(
        df_sales, 
        'Setor', 
        filtrar_setor
    )

    df_sales = filtrar_df(
        df_sales, 
        'Canal_de_Vendas', 
        filtrar_canal_de_vendas
    )

    if data_inicio and data_fim:

        df_sales = df_sales[
            (df_sales['Data_Venda'] >= data_inicio) & 
            (df_sales['Data_Venda'] <= data_fim)
        ]

    return df_sales

st.set_page_config(layout='wide')

with st.spinner('Puxando dados do Phoenix...'):

    if not 'df_sales' in st.session_state:

        gerar_df_sales()

st.title('Análise - Data Venda vs Data Execução')

st.divider()

st.header('Filtros')

row_filtros = st.columns(3)

row_periodo = st.columns(2)

filtrar_base_luck, filtrar_setor, filtrar_canal_de_vendas, data_inicio, data_fim = colher_filtros_escolhidos(row_filtros, row_periodo)

df_sales = aplicar_filtros_escolhidos()

df_sales['Intervalo'] = (pd.to_datetime(df_sales['Data_Execucao']) - pd.to_datetime(df_sales['Data_Venda'])).dt.days

df_sales.rename(
    columns={
        'Base_Luck': 'Base Luck',
        'Canal_de_Vendas': 'Canal de Vendas',
        'Data_Venda': 'Data Venda',
        'Data_Execucao': 'Data Execução',
        'Intervalo': 'Intervalo (dias)'
    },
    inplace=True
)

st.divider()

st.title('Análise')

st.header('Geral')

st.subheader(f"Intervalo Médio entre Data da Venda e Data de Execução dos Serviços = {df_sales['Intervalo (dias)'].mean():.1f} dias")

row_resultados = st.columns(3)

with row_resultados[0]:

    st.header('Por Base Luck')

    df_grouped = df_sales.groupby('Base Luck')['Intervalo (dias)'].mean().reset_index()

    df_grouped['Intervalo (dias)'] = round(
        df_grouped['Intervalo (dias)'], 
        1
    )

    st.dataframe(
        df_grouped,
        hide_index=True,
        use_container_width=True
    )

with row_resultados[1]:

    st.header('Por Setor')

    df_grouped = df_sales.groupby('Setor')['Intervalo (dias)'].mean().reset_index()

    df_grouped['Intervalo (dias)'] = round(
        df_grouped['Intervalo (dias)'], 
        1
    )

    st.dataframe(
        df_grouped,
        hide_index=True,
        use_container_width=True
    )

with row_resultados[2]:

    st.header('Por Canal de Vendas')

    df_grouped = df_sales.groupby('Canal de Vendas')['Intervalo (dias)'].mean().reset_index()

    df_grouped['Intervalo (dias)'] = round(
        df_grouped['Intervalo (dias)'], 
        1
    )

    st.dataframe(
        df_grouped,
        hide_index=True,
        use_container_width=True
    )

st.divider()

st.title('Detalhamento')

st.dataframe(
    df_sales,
    hide_index=True,
    use_container_width=True
)
