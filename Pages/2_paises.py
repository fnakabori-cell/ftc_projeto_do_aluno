# bibliotecas necessárias
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium
import inflection
import re
import importlib
import sys
from pathlib import Path

st.set_page_config(
    page_title='Paises', page_icon='🌎', layout='wide')

# ===========================================================================
#Funções
# ===========================================================================
# FUNÇÃO 1 - NOME DOS PAÍSES
COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zealand",
    162: "Philippines",
    166: "Qatar",
    184: "Singapore",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "United Kingdom",
    216: "United States"
}

def country_name(country_id):
    return COUNTRIES.get(country_id)

# FUNÇÃO 2 - CATEGORIA DE PREÇO
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    elif price_range == 4:
        return "gourmet"
    else:
        return None

# FUNÇÃO 3 - NOME DAS CORES
COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

def color_name(color_code):
    return COLORS.get(color_code)

# FUNÇÃO 4 - RENOMEAR COLUNAS
def rename_columns(dataframe):
    df1 = dataframe.copy()

    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df1.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new
    return df1

# FUNÇÃO 5 - REMOVER ESPAÇOS EXTRAS DOS TEXTOS
def remover_espacos(dataframe):
    df1 = dataframe.copy()

    # Identificar todas as colunas de texto
    colunas_texto = df1.select_dtypes(
        include=['object', 'str']
    ).columns

    # Remover espaços no início e no final dos textos
    for coluna in colunas_texto:
        df1[coluna] = df1[coluna].map(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    return df1



# União das funções para carregar todas de uma vez
def apply_func(df1):
    # FUNÇÃO 1 - NOME DOS PAÍSES
    df1['Country'] = df1['Country Code'].apply(lambda x: country_name(x))

    # FUNÇÃO 2 - CATEGORIA DE PREÇO
    df1['Price range'] = df1.loc[:, 'Price range'].apply(lambda x: create_price_tye(x))

    # FUNÇÃO 3 - CORES
    df1['Expressed color'] = df1.loc[:, 'Rating color'].apply(lambda x: color_name(x))

    # FUNÇÃO 4 - RENOMEAR COLUNAS
    df1 = rename_columns(df1)

    # FUNÇÃO 5 - REMOVER ESPAÇOS EXTRAS
    df1 = remover_espacos(df1)

    # TRATAMENTO DE CULINÁRIAS
    df1['cuisines'] = df1['cuisines'].apply(
        lambda x: x.split(",")[0].strip() if isinstance(x, str) else x
    )

    return df1

# Função para remover coluna, registros e duplicatas
def clean_code(df1):

    # Removendo coluna inútil
    df1 = df1.drop(labels=['switch_to_order_menu'], axis='columns')

    # Removendo registros sem culinária
    df1 = df1.dropna(subset=['cuisines']).copy()

    # Excluindo registros conforme o professor
    df1 = df1.loc[df1['cuisines'] != 'Drinks Only', :].copy()
    df1 = df1.loc[df1['cuisines'] != 'Mineira', :].copy()

    # Removendo duplicatas
    df1 = df1.drop_duplicates().reset_index(drop=True)

    return df1

def bar_1(df1):
    re2 = df1.loc[:,['restaurant_id','country']].groupby(['country']).count().sort_values(by='restaurant_id',ascending=False).reset_index()
    fig = px.bar(re2, x='country',y='restaurant_id',text_auto=True,labels={'country':'Países','restaurant_id':'Quantidade de Restaurantes'},title='Quantidade de Restaurantes Registrados por País')
    return fig

def bar_2(df1):
    re1 = df1.loc[:,['country','city','restaurant_id']].groupby(['country','city']).count().sort_values(by='country',ascending=False).reset_index()
    re1 = re1.loc[:,['country','city']].groupby(['country']).count().sort_values(by='city',ascending=False).reset_index()
    fig = px.bar(re1, x='country',y='city',text_auto=True,labels={'country':'Países','city':'Quantidade de Cidades'},title='Quantidade de Cidades Registradas por País')
    return fig


def bar_3(df1):
    re8 = round(df1.loc[:,['votes','country']].groupby(['country']).mean().sort_values(by='votes',ascending=False).reset_index(),2)
    fig = px.bar(re8, x='country',y='votes',text_auto=True,labels={'country':'Países','votes':'Quantidade de Avaliações'},title='Média de Avaliações feitas por País')
    return fig


def bar_4(df1):
    re11 = round(df1.loc[:,['average_cost_for_two','country']].groupby(['country']).mean().sort_values(by='average_cost_for_two',ascending=False).reset_index(),2)
    fig = px.bar(re11, x='country',y='average_cost_for_two',text_auto=True,labels={'country':'Países','average_cost_for_two':'Preço de prato para duas Pessoas'},title='Média do Preço de um prato para duas pessoas por País')
    return fig

    

# --------------------- Início da Estrutura Lógica do Código ---------------
# ===========================================================================
#Importar os dados
#==========================================================================
df = pd.read_csv('dataset/zomato.csv')
df1 = df.copy()

# ===========================================================================
#Limpando os dados
#==========================================================================
df1 = apply_func(df1)
df1 = clean_code(df1)



# ===========================================================================
#Barra lateral
#==========================================================================
#path = 'logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image,width=250)

st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown('## Filtros')


country = ['Philippines', 'Brazil', 'Australia', 'United States of America',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey']
country_op = st.sidebar.multiselect('Escolha os Países que Deseja visualizar as informações',
                      country,
                      default=['Brazil','England','Qatar', 'South Africa','Canada','Australia'])

#Filtro de cidades
df1 = df1.loc[df1['country'].isin(country_op),:]




# ===========================================================================
#Layout no Streamlit
#==========================================================================
st.markdown('# 🌎 Visão Países')

#Primeiro container com um gráfico
with st.container():
    fig = bar_1(df1)
    st.plotly_chart(fig,use_container_width=True,theme=None)
    
    
#Segundo container com um gráfico
with st.container():
    fig = bar_2(df1)
    st.plotly_chart(fig,use_container_width=True,theme=None)
    

#Terceiro container com duas colunas, cada qual com um gráfico
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        fig = bar_3(df1)
        st.plotly_chart(fig,use_container_width=True,theme=None)
        
        
    with col2:
        fig = bar_4(df1)
        st.plotly_chart(fig,use_container_width=True,theme=None)