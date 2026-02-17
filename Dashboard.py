import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

data_atual = datetime.now()
ano_atual = data_atual.year

st.set_page_config(page_title='Gestão de Vendas', layout='wide')

def formatar_numero(valor, prefixo = ''):
    for unidade in ['', 'Mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} Milhões'


st.title('DASHBOARD DE VENDAS 🛍️')

# Capturando dados
url = 'https://labdados.com/produtos'

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

with st.sidebar:
    st.title('Filtros')

    regiao = st.selectbox('Regioão', regioes)

    if regiao == 'Brasil':
        regiao = ''
        
    todos_anos = st.checkbox('Dados de todo o periodo', value=True)

    if todos_anos:
        ano = ''
    else:
        ano = st.slider('Ano', 2020, ano_atual)

query_string = {'regiao':regiao.lower(), 'ano':ano}
response = requests.get(url,params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') 

filtro_vendedores = st.sidebar.multiselect('Vendedores',dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
### tabelas de receitas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### tabelas de quantidade
qtd_vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
qtd_vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat', 'lon']].merge(qtd_vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

qtd_vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
qtd_vendas_mensal['Ano'] = qtd_vendas_mensal['Data da Compra'].dt.year
qtd_vendas_mensal['Mes'] = qtd_vendas_mensal['Data da Compra'].dt.month_name()

qtd_vendas_categoria = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

### tabela vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))


## graficos
### graficos receita

fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,receita_mensal.max()),
                             color='Ano',
                             line_dash= 'Ano',
                             title='Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estado = px.bar(receita_estados.head(),
                            x='Local da compra',
                            y='Preço',
                            text_auto=True,
                            title='Top Estados (Receita)')

fig_receita_estado.update_layout(yaxis_title = 'Receita')

fig_receita_categoria = px.bar(receita_categoria.head(),
                               text_auto=True,
                               title='Top Categorias (Receita)')

fig_receita_categoria.update_layout(yaxis_title = 'Receita')

### grafico quantidade vendas
fig_mapa_quantidade_vendas = px.scatter_geo(qtd_vendas_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Quantidade Vendas por Estado')

fig_quantidade_vendas_mensal = px.line(qtd_vendas_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,qtd_vendas_mensal.max()),
                             color='Ano',
                             line_dash= 'Ano',
                             title='Quantidade Vendas Mensal')

fig_quantidade_vendas_mensal.update_layout(yaxis_title = 'Quantidade Vendas')

fig_quantidade_vendas_estado = px.bar(qtd_vendas_estados.head(),
                            x='Local da compra',
                            y='Preço',
                            text_auto=True,
                            title='Top Estados (Quantidade Vendas)')

fig_quantidade_vendas_estado.update_layout(yaxis_title = 'Quantidade Vendas')

fig_quantidade_vendas_categoria = px.bar(qtd_vendas_categoria.head(),
                               text_auto=True,
                               title='Top Categorias (Quantidade Vendas)')

fig_quantidade_vendas_categoria.update_layout(yaxis_title = 'Quantidade Vendas')

## Visualização no streamlit
# colunas no site
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])


with aba1:
    col_1, col_2 = st.columns(2)
    with col_1: 
        st.metric('Receita', formatar_numero(dados['Preço'].sum(),'R$'), help='Soma de todas as vendas')
        st.plotly_chart(fig_mapa_receita)
        st.plotly_chart(fig_receita_estado)
    with col_2:
        st.metric('Quantidade de Vendas', formatar_numero(dados.shape[0]), help='Quantidade de linhas da base de dados.')
        st.plotly_chart(fig_receita_mensal)
        st.plotly_chart(fig_receita_categoria)

with aba2:
    col_1, col_2 = st.columns(2)
    with col_1: 
        st.metric('Receita', formatar_numero(dados['Preço'].sum(),'R$'), help='Soma de todas as vendas')
        st.plotly_chart(fig_mapa_quantidade_vendas)
        st.plotly_chart(fig_quantidade_vendas_estado)
        
    with col_2:
        st.metric('Quantidade de Vendas', formatar_numero(dados.shape[0]), help='Quantidade de linhas da base de dados.')
        st.plotly_chart(fig_quantidade_vendas_mensal)
        st.plotly_chart(fig_quantidade_vendas_categoria)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores',2, 10, 5)
    col_1, col_2 = st.columns(2)
    with col_1: 
        st.metric('Receita', formatar_numero(dados['Preço'].sum(),'R$'), help='Soma de todas as vendas')
        fig_receita_vendedores=px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                      x='sum',
                                      y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                      text_auto=True,
                                      title=f'Top {qtd_vendedores} vendedores (Receita)')
        
        st.plotly_chart(fig_receita_vendedores)
    with col_2:
        st.metric('Quantidade de Vendas', formatar_numero(dados.shape[0]), help='Quantidade de linhas da base de dados.')
        fig_qtd_vendedores=px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                      x='count',
                                      y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                      text_auto=True,
                                      title=f'Top {qtd_vendedores} vendedores (Quantidade de Vendas)')
        
        st.plotly_chart(fig_qtd_vendedores)
        
## teste de video
# url_video = 'https://www.youtube.com/watch?v=9vGSnnq6pY8'
# st.video(url_video)

# tabela
st.title('Detalhes')
st.dataframe(dados)
