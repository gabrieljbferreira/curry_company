import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home")

image_path = "logo.jpg"
image = Image.open( image_path )
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write( "# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard was build to follow up the growth metrics of the Company, Deliverers and Restaurants.
    
    ### How to use this Growth Dashboard
    - Company Vision
        - Managerial View: overall behavior metrics
        - Tactical View: weekly growth metrics
        - Geographic View: Geolocation insights
    - Deliverer Vision
        - Follow up weekly growth metrics
    - Restaurant Vision
        - Weekly growth metrics of the restaurants
    ### Ask for Help
    Gabriel Junqueira - @gabrieljbferreira"""
)