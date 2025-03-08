# Libraries
import re
import pandas as pd
import numpy as np
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

#====================================================================
# Functions

def avg_std_time_on_traffic(df):
    df_aux = df.loc[ : , ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City' , 'Road_traffic_density']).agg( {'Time_taken(min)' : ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', 
                    color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig
            
def avg_std_time_graph(df):
    df_aux = df.loc[ : , ['City', 'Time_taken(min)']].groupby('City').agg( {'Time_taken(min)' : ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y= dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig

def avg_std_time_delivery(df , festival, op):
    """
    This function calculates the average time and standard deviation of delivery time
    Parameters:
        Input: df: Dataframe with necessary data for calculation
                op: Operation required
                    'avg_time': Mean time
                    'std_time': Standard Deviation time
        Output: Dataframe with 2 columns and 1 row
    """
    df_aux = df.loc[ : , ['Time_taken(min)', 'Festival']].groupby('Festival').agg( {'Time_taken(min)' : ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, 'avg_time'], 2).values[0]

    return df_aux

def distance(df , fig):
    if fig ==False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']         
        df['distance'] = df.loc[0:10, cols].apply( lambda x:
                                        haversine(
                                            (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ),
                                            axis=1
                                        )
        average_distance = df['distance'].mean()
        st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{round(average_distance, 2)}</h3>", unsafe_allow_html=True)
        
        return average_distance
    
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df['distance'] = df.loc[0:10, cols].apply( lambda x:
                                        haversine(
                                            (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ),
                                            axis=1
                                        )
        average_distance = df.loc[: , ['City', 'distance']].groupby('City').mean().reset_index()

        fig = go.Figure(data= [go.Pie(labels=average_distance['City'], values=average_distance['distance'], pull=[0.1, 0, 0])])
        
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

#Import dataset
df = pd.read_csv("dataset/train.csv", encoding="utf-8")

# Limpeza de dados / Data Cleaning
df = clean_code(df)

#=============================================================================

# Market Place - Visão Entregadores | Marketplace - Deliverers Vision

st.header( 'Marketplace - Restaurants Vision')

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
# Layout

tab1, = st.tabs(['Managerial View'])

with tab1:
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )

        with col1:
            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Unique Deliverers</p>", unsafe_allow_html=True)
            delivery_unique = len(df.loc[: , 'Delivery_person_ID'].unique())

            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{delivery_unique}</h3>", unsafe_allow_html=True)

        with col2:
            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Average Distance</p>", unsafe_allow_html=True)
            average_distance = distance(df , fig=False)
            
        with col3:
            df_aux = avg_std_time_delivery( df, 'Yes', 'avg_time')           

            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Avg Dlv Time in Festival</p>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{round(df_aux, 2)}</h3>", unsafe_allow_html=True)
            
        with col4:
            df_aux = avg_std_time_delivery( df, 'Yes', 'std_time')

            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Std Dlv Time in Festival</p>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{round(df_aux, 2)}</h3>", unsafe_allow_html=True)
            
        with col5:
            df_aux = avg_std_time_delivery( df, 'No', 'avg_time')

            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Avg Dlv Time out Festival</p>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{round(df_aux, 2)}</h3>", unsafe_allow_html=True)

        with col6:
            df_aux = avg_std_time_delivery( df, 'No', 'std_time')

            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 15px;'>Std Dlv Time out Festival</p>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; font-size: 32px;'>{round(df_aux, 2)}</h3>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True) # Add space between containers

    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 25px;'>Time Distribution per City</p>", unsafe_allow_html=True)

            fig = avg_std_time_graph(df)
            st.plotly_chart( fig )

        with col2:
            st.markdown("<p style='text-align: center; font-weight: bold; font-size: 25px;'>Average Time per Type of Delivery</p>", unsafe_allow_html=True)

            fig = avg_std_time_on_traffic(df)
            st.plotly_chart( fig )

    with st.container():
        st.markdown("<p style='text-align: center; font-weight: bold; font-size: 25px;'>Distribution of Average Distance per City</p>", unsafe_allow_html=True)

        fig = distance(df, fig=True)
        st.plotly_chart( fig )

    with st.container():
        st.markdown("<p style= 'text-align: center; font-weight: bold; font-size: 25px;'>Average Delivery Time per City and Traffic </p>", unsafe_allow_html=True)

        cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
        df_aux = df.loc[ : , cols].groupby(['City' , 'Road_traffic_density']).agg( {'Time_taken(min)' : ['mean', 'std']} )
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        df_html = df_aux.to_html(index=False)  # Remove o índice

        st.markdown(f"""
            <div style="display: flex; justify-content: center;">
                {df_html}
            </div>
        """, unsafe_allow_html=True)