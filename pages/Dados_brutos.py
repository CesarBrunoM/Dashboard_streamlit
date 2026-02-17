import streamlit as st
import requests
import pandas as pd
import time
import io


icon = r'C:\Users\bruno.lima\Music\streamlit\Image\shopping_cart_checkout.png'

@st.cache_data
def converte_excel(df, formato):
    if formato == 'csv':
        return df.to_csv(index=False).encode('utf-8')
    
    else:  # xlsx
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()
    
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(3)
    sucesso.empty()
    
        
st.title('DADOS BRUTOS')
st.set_page_config(page_title='Gestão de Vendas', page_icon=icon,layout='wide')

url = 'https://labdados.com/produtos'
avaliacao_lista = [1,2,3,4,5]

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))
    
with st.sidebar:
    st.title('Filtros')
    
    with st.expander('Nome do produto'):
        produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
        
    with st.expander('Preço do produto'):
        preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
        
    with st.expander('Frete'):
        frete = st.slider('Selecione o valor do frete', 0, int(dados['Frete'].max()), (0,int(dados['Frete'].max()+10)))
        
    with st.expander('Data da Compra'):
        data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
     
    with st.expander('Categoria do produto'):
        categoria_produtos = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
        
    with st.expander('Vendedor'):
        vendedor = st.multiselect('Selecione o Vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())

    with st.expander('Local da Compra'):
        local_compra = st.multiselect('Selecione o Local da Compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
    
    with st.expander('Tipo de pagamento'):
        tipo_pagamento = st.multiselect('Selecione o tipo de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
        
    # with st.expander('Quantidade de Parcelas'):
    qtd_parcelas = st.slider('Quantidade de parcelas', dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max(), (dados['Quantidade de parcelas'].min(), 
                                                                                                                                               dados['Quantidade de parcelas'].max()))
    
    avaliacao = st.slider('Avaliação', dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max(), (dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max()))
    # st.markdown('Avaliação')    
    # avaliacao = st.feedback('stars')
    # if avaliacao is None:
    #     pass
    
    query = '''
        Produto in @produtos and \
        `Categoria do Produto` in @categoria_produtos and \
        @preco[0] <= Preço <= @preco[1] and \
        @frete[0] <= Frete <= @frete[1] and \
        @data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
        Vendedor in @vendedor and \
        `Local da compra` in @local_compra and \
        @avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
        `Tipo de pagamento` in @tipo_pagamento and \
        @qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
        '''
    
    dados_filtrados = dados.query(query)
    dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]} colunas]')

st.markdown('Informe o nome do arquivo')
coluna_1, coluna_2 = st.columns(2)
with coluna_1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
with coluna_2:
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download em xlsx",
            data=converte_excel(dados_filtrados, 'xlsx'),
            file_name=f"{nome_arquivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            on_click = mensagem_sucesso
        )
    with col2:
        st.download_button(
            label='Download em csv', 
            data = converte_excel(dados_filtrados, 'csv'), 
            file_name = f'{nome_arquivo}.csv', 
            mime = 'text/csv', 
            on_click = mensagem_sucesso
        )
    
# with coluna_2:
#     st.download_button(
#         'Fazer o download em csv', 
#         data = converte_excel(dados_filtrados, 'csv'), 
#         file_name = f'{nome_arquivo}.csv', 
#         mime = 'text/csv', 
#         on_click = mensagem_sucesso
#     )
# with coluna_3:
#     st.download_button(
#         label="Fazer o download",
#         data=converte_excel(dados_filtrados, 'xlsx'),
#         file_name=f"{nome_arquivo}.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
