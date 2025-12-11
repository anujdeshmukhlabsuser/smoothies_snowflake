# Import python packages
import streamlit as st
import snowpark
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.write(
  """
  Choose the fruits you want in your Smoothie.
  """
)

name_on_smoothie = st.text_input("Name on the Smoothie ")
st.write("The name on your Smoothie will be : ", name_on_smoothie)

# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# --- FIX 1: Convert Snowpark Dataframe to Pandas so Streamlit can use it ---
pd_df = my_dataframe.to_pandas()

ingredient_list = st.multiselect(
    'Choose up to 5 ingredients',
    pd_df['FRUIT_NAME'],
    max_selections= 5# pass the specific column from the pandas dataframe
)

ingredient_string = ''
if ingredient_list:
    for fruit_choosen in ingredient_list:
        ingredient_string += fruit_choosen + ' '

    my_insert_stmt = """ insert into smoothies.public.orders(name_on_order,ingredients)
                values ('""" + name_on_smoothie + """','""" + ingredient_string + """');"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if ingredient_string:
            session.sql(my_insert_stmt).collect()
            
            # --- FIX 2: Use an f-string to combine the text and variable ---
            st.success(f'Your Smoothie is ordered, {name_on_smoothie}!', icon="✅")
