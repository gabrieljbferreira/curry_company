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

#====================================================================
# Functions

def top_delivers(df, top_asc): 
    df2 = ( df.loc[: , ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby( ['City', 'Delivery_person_ID']).max()
                                                                        .sort_values( ['City', 'Time_taken(min)'], ascending=False)
                                                                        .reset_index() )
    #Somente os 10 primeiros por cidade / Highlight Top 10
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian' , :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban' , :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban' , :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03]).reset_index( drop=True)
    df3.columns = ['City', 'Deliverer ID', 'Min Taken']
    
    return df3

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

#Import dataset
df = pd.read_csv("dataset/train.csv", encoding="utf-8")

# Limpeza de dados / Data Cleaning
df = clean_code(df)

#=============================================================================

# Market Place - Visão Entregadores | Marketplace - Deliverers Vision

st.header( 'Marketplace - Deliverers Vision')

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

#============================================================================
#Layout

tab1, = st.tabs(['Managerial Vision'])

with tab1:
    with st.container():
        col1, col2, col3, col4 = st.columns( 4 , gap='large')

        with col1:
            oldest = df.loc[: , 'Delivery_person_Age'].max()
            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Oldest Deliverer</p>", unsafe_allow_html=True)

            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{oldest}</h3>", unsafe_allow_html=True)
        with col2:
            youngest = df.loc[: , 'Delivery_person_Age'].min()

            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Youngest Deliverer</p>", unsafe_allow_html=True)

            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{youngest}</h3>", unsafe_allow_html=True)
        with col3:
            best_vehicle = df.loc[: , 'Vehicle_condition'].max()

            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Best Vehicle Cond</p>", unsafe_allow_html=True)

            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{best_vehicle}</h3>", unsafe_allow_html=True)
        with col4:
            worst_vehicle = df.loc[: , 'Vehicle_condition'].min()

            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Worst Vehicle Cond</p>", unsafe_allow_html=True)

            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{worst_vehicle}</h3>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True) # Add space between containers
    
    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 25px;'>Average Rates per Deliverer</p>", unsafe_allow_html=True)

            avg_deliv = df.loc[: , ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            avg_deliv.columns = ['Deliverer ID', 'Ratings']

            st.dataframe( avg_deliv )

        with col2:
            #Average Rates - Traffic Condition
            st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 25px;'>Avg Rates - Traffic Condition</p>", unsafe_allow_html=True)

            df_agg_ratings_by_traffic = df.loc[: , ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg( {'Delivery_person_Ratings' : ['mean', 'std']})
            
            # Renomear as colunas para ficar mais organizado / Rename columns to organize
            df_agg_ratings_by_traffic.columns = ['Delivery Mean', 'Delivery Std']
            df_agg_ratings_by_traffic.reset_index()

            st.dataframe (df_agg_ratings_by_traffic)

            #Average Rates - Weather Condition
            st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 25px;'>Avg Rates - Weather Condition</p>", unsafe_allow_html=True)

            df_agg_ratings_by_weather = ( df.loc[: , ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions')
                              .agg( {'Delivery_person_Ratings' : ['mean', 'std']}) )
          
            # Renomear as colunas para ficar mais organizado / Rename columns to organize
            df_agg_ratings_by_weather.columns = ['Delivery Mean', 'Delivery Std']
            df_agg_ratings_by_weather.reset_index()

            st.dataframe(df_agg_ratings_by_weather)
            

    with st.container():
        col1, col2 = st.columns (2)

        with col1:
            st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 25px;'>Top 10 Fastest Deliverers</p>", unsafe_allow_html=True)
            df3 = top_delivers(df , top_asc=True)   
            st.dataframe(df3)

        with col2:
            st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 25px;'>Top 10 Slowest Deliverers</p>", unsafe_allow_html=True)
            df3 = top_delivers(df , top_asc=False)
            st.dataframe(df3)