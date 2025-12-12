# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# --- UI TWEAK: Add a page title and icon ---
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

name_on_smoothie = st.text_input("Name on the Smoothie:")

# --- DATA CONNECTION ---
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

# Convert to Pandas
pd_df = my_dataframe.to_pandas()

# --- UI TWEAK: Hide the raw data table in an expander ---
# This keeps the UI clean but lets you check data if needed
with st.expander("See available fruit data"):
    st.dataframe(pd_df)

# --- THE INPUTS ---
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

if ingredient_list:
    ingredient_string = ''

    for fruit_chosen in ingredient_list:
        ingredient_string += fruit_chosen + ' '
        
        # Look up the SEARCH_ON value for the specific fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # --- UI TWEAK: Display Nutrition Info cleanly ---
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Call the API using the correct search_on term
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Could not fetch data for {fruit_chosen}")

    # --- SUBMIT BUTTON ---
    my_insert_stmt = """ insert into smoothies.public.orders(name_on_order,ingredients)
            values ('""" + name_on_smoothie + """','""" + ingredient_string + """');"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if ingredient_string:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_smoothie}!', icon="✅")
