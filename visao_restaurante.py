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
import numpy as np
import plotly.graph_objects as go

#------------------------------------------------------
#funções
#------------------------------------------------------
def clean_code (df1):
    """ Esta função tem esponsabilidade de limpar o dataframe
    
    Tipos de limpeza:
    1 Remoção de dados NaN
    2 Mudança da vaiável das colunas
    3 Remoção dos espaços nas colunas que contem texto
    4 Fomatação das colunas datas
    5 limpeza da coluna de tempo (timetaken(min))
    
    INPUT: dataframe
    OUTPUT: dataframe
    """
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
return df1

#--------------------------Inicio estrutura de dados-----------------------

#---------------------------------------------
#import file csv
#---------------------------------------------
df = pd.read_csv('dataset/train.csv')

#---------------------------------------------
#Limpando dados
#---------------------------------------------
df1 = clean_code(df)


    
# Graph bar
#columns
cols = ['ID', 'Order_Date']

#lines
df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

px.bar( df_aux, x='Order_Date', y='ID' )

#=============================
#Side Bar
#=============================

#image_path = '/Users/Gus/Documents/repos/FTC/logo.png'
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

st.header('Dashboard - Visão Restaurantes')
tab1,  = st.tabs(["Visão Gerencial"])

with tab1:
    with st.container():
        st.markdown('#### Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len( df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Ent. Únicos', delivery_unique)
            
        with col2:
            cols = ['Delivery_location_latitude','Delivery_location_longitude', 'Restaurant_longitude', 'Restaurant_latitude']

            df1['distance'] = df1.loc[:, cols].apply( lambda x:
                      haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                       (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

            avg_distance = np.round(df1['distance'].mean(),2)
            col2.metric('Distância média:',avg_distance )
            
            
        with col3:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg( {'Time_taken(min)': ['mean', 'std']} ))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes ', 'avg_time'],2)
            col3.metric('Tempo Médio Festival', df_aux)
            
        with col4:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg( {'Time_taken(min)': ['mean', 'std']} ))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes ', 'std_time'],2)
            col4.metric('Desvio Pad. Festival', df_aux)
            
        with col5:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg( {'Time_taken(min)': ['mean', 'std']} ))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No ', 'avg_time'],2)
            col5.metric('Desvio Pad. S/ Festival', df_aux)
            
        with col6:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                         .groupby('Festival')
                         .agg( {'Time_taken(min)': ['mean', 'std']} ))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No ', 'std_time'],2)
            col6.metric('Desvio Pad. S/ Festival', df_aux)
    st.markdown("""---""")
        
    with st.container():
        st.markdown("#### Tempo médio de entrega por cidade")
        
        df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg( {'Time_taken(min)' : ['mean', 'std']} )
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        fig = go.Figure()
        fig.add_trace( go.Bar( name='Control',
                                   x=df_aux['City'],
                                   y=df_aux['avg_time'],
                                   error_y=dict( type='data', array=df_aux['std_time'] ) ) )
        fig.update_layout(barmode='group')
        st.plotly_chart(fig)
        
    st.markdown("""---""")
        
    with st.container():
        st.markdown("#### Distribuição do Tempo")
        col1, col2,  = st.columns(2)
        with col1:
            st.markdown('##### Tempo Médio e Desvio Padrão')
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1.loc[:, cols ].apply( lambda x:
                                                      haversine(  (x['Restaurant_latitude'] , x['Restaurant_longitude']),
                                                                  (x['Delivery_location_latitude'] , x['Delivery_location_longitude']) ), axis=1)

            avg_distance = df1.loc[:,['City', 'distance']].groupby('City').mean().reset_index()

            fig = go.Figure( data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'],pull =[0, 0.1, 0])])
            st.plotly_chart(fig)
            
        with col2:
            st.markdown('#### SunBurst')
            
            df_aux = df1.loc[:, ['City','Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)' : ['mean', 'std']} )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))

            st.plotly_chart(fig)
            
    st.markdown("""---""")
        
    with st.container():
        st.markdown("#### Distribuição da Distância")
        cols = ['City','Time_taken(min)', 'Type_of_order']
        df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)' : ['mean', 'std']} )

        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        st.dataframe(df_aux)