# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests  
import pandas

st.title(":cup_with_straw: Customize Your Smoothie! ")
st.write(
  """
  Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name the Smoothie")
st.write("The name of the smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")

session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('search_on'))
# st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_dataframe.to_pandas()

ingredient_list = st.multiselect(
    'Chose up to 5 ingredients:',
    my_dataframe,
    max_selections = 5
)
if len(ingredient_list) == 4:
    st.warning('Careful! You have chosen 4 ingredients. You can only add 1 more! 🛒')

if ingredient_list:    
    ingredients_string = ''

    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + " Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")  
        st_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, NAME_ON_ORDER)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")

