# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched
import requests
import pandas as pd

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(":boom: Mel's Custom Smoothies :boom:")
# MLT: Write a formatted markdown string to the screen.
st.write(
    """
    **Choose the fruits you want in your custom
    Smoothie!** 
    """
)

#Orignal session created in snowflake
#session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

#Convert the snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

##My Addition
name_on_order = st.text_input('Name on Smoothie: ')
st.write('The name on your Smoothie will be: ', name_on_order)

# st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list = st.multiselect(
    'Chose up to 5 ingredients: ',
    my_dataframe,label_visibility="visible",help="Please select a maximum of 5 fruits.",
    placeholder="Drop down to see fruits",max_selections=5)
if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)

    ingredients_string = ''
    for fruit_chosen in ingredients_list: 
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on,'.')
        st.subheader(fruit_chosen + ': Nutritional Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
    values('""" + ingredients_string + """','"""+name_on_order+"""')"""

    #returns for st.button is true if it is clicked..
    time_to_insert = st.button('Submit Order')
    #collect() returns the df as a list and not a df
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(name_on_order + ', your smoothie is ordered!', icon="✅")



        
