# Libraries
import re
import pandas as pd
import haversine as haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

#Import dataset
df_raw = pd.read_csv("dataset/train.csv", encoding="utf-8")

# Fazer uma cópia do DF lido / Make a copy of dataframe
df = df_raw.copy()

#====================================================================
# Functions
def country_maps(df):
    df_aux = df.loc[: , ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude'] ].groupby(['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )

    folium_static( map, width=1024, height=600)

def order_share_by_week(df):
    df_aux1 = df.loc[: , ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df.loc[: , ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line( df_aux, x='week_of_year', y='order_by_deliver')

    return fig

def order_by_week(df):        
    # criar coluna semana / Create Week Column
    df['week_of_year'] = df['Order_Date'].dt.strftime( '%U')
    df_aux = df.loc[: , ['ID', 'week_of_year']].groupby( 'week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def traffic_order_city(df):
    df_aux = df.loc[: , ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
                
    return fig

def traffic_order_share(df):
    df_aux = df.loc[: , ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN ', : ]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

def order_metric(df):
    cols = ['ID', 'Order_Date']
    df_aux = df.loc[: , cols].groupby('Order_Date').count().reset_index()
    fig = px.bar( df_aux, x='Order_Date', y='ID')

    return fig

def clean_code(df):
    """This function has the responsibility of cleaning the dataframe

        Input: Dataframe
        Output: Dataframe
    """
    # Excluir linhas com idade dos entregadores vazia / Delete empty rows in age column
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Excluir NaN no Road Traffic / Delete 'NaN' in Road Traffic
    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Excluir NaN no City / Delete 'NaN' in City
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Excluir NaN no Festival / Delete 'NaN' in Festival
    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Conversão de texto/categora/string para numeros inteiros / Convert strings to int
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    # Conversão de texto para numeros decimais / Convert text to float
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    # Conversão de texto para data / Convert text to date format
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format = '%d-%m-%Y')

    # Remove as linhas da coluna multiple_deliveries que tenham o conteudo igual a 'NaN ' / Delete 'NaN' in Multiple Deliveries
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    # Remover espaço da string / Remove space from strings (trim)
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()

    # Comando para remover o texto de numeros / Remove text from numbers
    df.loc[: , 'Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df.loc[: , 'Time_taken(min)'] = df.loc[: , 'Time_taken(min)'].astype( int )

    return df
#====================================================================
#------------------- Beginning of code's logical structure-----------------------

# Limpeza de dados / Data Cleaning
df = clean_code( df )

#=============================================================================

# Market Place - Visão Cliente | Marketplace - Client Vision

st.header( 'Marketplace - Client Vision')

image_path = 'logo.jpg'
image = Image.open( image_path )
st.sidebar.image( image, width=150 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Select a Limit Date')

#============================================================================
#Date Slider

date_slider = st.sidebar.slider ( 'Until which date?' ,
                                     value= datetime( 2022, 3, 13),
                                     min_value= datetime(2022, 2, 11),
                                     max_value= datetime(2022, 4, 6),
                                     format='DD-MM-YYYY' )

#============================================================================

#Multiselect Traffic Conditions

st.sidebar.markdown( '## Select desired Traffic Conditions')
traffic_options = st.sidebar.multiselect('', ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")

#============================================================================
#Multiselect Weather Conditions

st.sidebar.markdown( '## Select desired Weather Conditions')
weather_options = df['Weatherconditions'].unique()
st.sidebar.multiselect( '', weather_options, default=weather_options)

#============================================================================
## Date Filter
selected_lines = df['Order_Date'] < date_slider
df = df.loc[selected_lines , :]

st.sidebar.markdown("""---""")

## Traffic density Filter
selected_lines = df['Road_traffic_density'].isin (traffic_options)
df = df.loc[selected_lines, :]

## Weather conditions Filter
selected_lines = df['Weatherconditions'].isin(weather_options)
df = df.loc[selected_lines , :]

st.sidebar.markdown("### Powered by Gabriel Junqueira")

#==============================================================================================
#Main Layout
tab1, tab2, tab3 = st.tabs( ['Managerial View', 'Tactical View', 'Geographic View'] )

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df)
        st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 30px;'>Orders by Day</p>", unsafe_allow_html=True)       
        st.plotly_chart( fig , use_container_width=True)
     
    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            fig = traffic_order_share(df)
            st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 30px;'>Orders - Traffic Density</p>", unsafe_allow_html=True)
            st.plotly_chart( fig , use_container_width=True)
          
        with col2:
            fig = traffic_order_city(df)
            st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 30px;'>Orders - City and Traffic</p>", unsafe_allow_html=True)
            st.plotly_chart( fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 30px;'>Orders by Week</p>", unsafe_allow_html=True)
        fig = order_by_week(df)
        st.plotly_chart( fig, use_container_width=True)

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True) # Add space between containers

    with st.container():
        fig = order_share_by_week(df)
        st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 30px;'>Order Deliveres by Week</p>", unsafe_allow_html=True)
        st.plotly_chart( fig, use_container_width=True)

with tab3:
    st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 30px;'>Country Map</p>", unsafe_allow_html=True)
    country_maps(df)