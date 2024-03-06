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

image_path = '/Users/Gus/Documents/repos/FTC/logo.png'
#image = Image.open ('image_path')
st.sidebar.image("/Users/Gus/Documents/repos/FTC/logo.png", width=150)

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
st.header('Dashboard - Visão Empresa')
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão geográfica"])


with tab1:
    st.markdown('### Orders by Day')
    cols = ['ID', 'Order_Date']

    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    fig = px.bar( df_aux, x='Order_Date', y='ID' )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""---""")
    
#Columns
    #col1, col2 = st.columns (2)
     #       with col1:
    st.markdown('### Traffic Order Share')
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig =  px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )
    st.plotly_chart(fig, user_container_width=True)
    st.markdown("""---""")               
                #with col2:
    st.markdown('### Traffic Order City')
    df_aux = df1.loc[:,['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    st.plotly_chart(fig, user_container_width=True)
    st.markdown("""---""")
    
with tab2:
    with st.container():
        st.markdown('### Orders by Week')
        df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%W' )
        cols = ['ID', 'week_of_year']
        df_aux = df1.loc[:, cols].groupby('week_of_year').count().reset_index()

        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, user_container_width=True)
    st.markdown("""---""")
    with st.container():
        st.markdown('### IDs by Week')
        df_aux01 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()

        df_aux = pd.merge(df_aux01, df_aux02, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig = px.line( df_aux, x='week_of_year', y='order_by_deliver' )
        st.plotly_chart(fig, user_container_width=True)
with tab3:
    st.markdown('### Delivery Map')
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
    folium_static( map, width=1024, height=600 )