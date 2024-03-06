#libraries 
import pandas as pd
from typing import MutableSet
import plotly.express as px
import folium
from haversine import haversine
from re import RegexFlag
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#import file csv
df = pd.read_csv('dataset/train.csv')

#ETL - clean dataset
df1 = df.copy()

#retirando os NaN da coluna delivery person age
linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

#removendo NaN do ratings
linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

#convertendo coluna delivery person ratings em decimal
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

#convertendo coluna order date em data
df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y' )

#convertendo coluna multiple deliveries em int
linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
#df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

#removendo os espaços das colunas
df1.loc[:,'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:,'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:,'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:,'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:,'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:,'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].str.strip()

#removendo nan do city
linhas_selecionadas = (df1['City'] != 'NaN')
df1 = df1.loc[linhas_selecionadas, :].copy()

#removendo nan do festival
linhas_selecionadas = (df1['Festival'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

#limpando a coluna de time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min) ', '', regex=False)

#removendo NaN
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str)
linhas_selecionadas = (df1['Time_taken(min)'] != 'nan')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# Graph bar
#columns
cols = ['ID', 'Order_Date']

#lines
df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

px.bar( df_aux, x='Order_Date', y='ID' )

#=============================
#Side Bar
#=============================

#image_path = 'logo.png'
#image = Image.open ('image_path')
st.sidebar.image("logo.png", width=150)

st.sidebar.markdown('# Cury company')
st.sidebar.markdown('#### Fatest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Select Limit Data')

date_slider = st.sidebar.slider(
        'How value?',
        value=pd.datetime( 2022, 4, 13),
        min_value=pd.datetime( 2022, 2, 11),
        max_value=pd.datetime( 2022, 4, 6),
        format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'What traffic condition?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Gustavo Correard')

#data filter
linhas_selcionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selcionadas, :]

#traffic filter
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#=============================
#Layout Streamlit
#=============================

st.header('Dashboard - Visão Entregadores')
tab1,  = st.tabs(["Visão Gerencial"])

with tab1:
    with st.container():
        st.markdown('### Overall Metrics')
        
        col1, col2, col3, col4 = st.columns( 4, gap='Large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade:', maior_idade)
                        
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade:', menor_idade)
                        
        with col3:
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Veículo:', melhor_veiculo)
                    
        with col4:
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Veículo:', pior_veiculo)
            
    with st.container():
        st.markdown("""---""")
        st.markdown('### Avaliações')
        
        col1, col2 = st.columns(2)
        with col1: 
            st.markdown('##### Avaliações Médias por Entregador')
            df_avg_ratings_per_deliver = df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)
        
        with col2:
            st.markdown('#### Avaliação da Média por Trânsito')
            df_avg_std_rating_by_traffic = (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']].groupby('Road_traffic_density')
                           .agg({'Delivery_person_Ratings' : ['mean', 'std']}))

            df_avg_std_rating_by_traffic.columns = ['delivery_mean','delivery_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
            
        
            st.markdown('#### Avaliação da Média por Clima')
            df_avg_std_rating_by_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions')
                     .agg({'Delivery_person_Ratings' : ['mean', 'std']}))


            df_avg_std_rating_by_weather.columns = ['delivery_mean','delivery_std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            
            st.dataframe(df_avg_std_rating_by_weather)
            
            
    with st.container():
        st.markdown("""---""")
        st.markdown('### Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        with col1: 
            st.markdown('##### Top Entregadores')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                      .groupby(['City', 'Delivery_person_ID'])
                      .min().sort_values(['City','Time_taken(min)'], ascending=True).reset_index())

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### Bottom Entregadores')

            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                      .groupby(['City', 'Delivery_person_ID'])
                      .max().sort_values(['City','Time_taken(min)'], ascending=False).reset_index())

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df3)