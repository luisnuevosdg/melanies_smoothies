# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import when_matched
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Pending Smoothie Orders ")
st.write(
  """
  Orders that need to be filled
  """
)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

my_dataframe = session.table("smoothies.public.orders") \
    .filter(col("ORDER_FILLED") == False) \
    .collect()

if len(my_dataframe)>0:
    editable_df = st.data_editor(my_dataframe)
else:
    st.success("No pending orders")

submitted = st.button('Submit')

if submitted:
    
    try:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)
        og_dataset.merge(edited_dataset
                         , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                         , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                        )
        st.success("Submitted", icon = "👍")
    
    except:
        st.success("Not submitted", icon = "❌")
