import streamlit as st
import pandas as pd
from src.database import get_all_vehicles
from src.i18n import TEXT

st.set_page_config(page_title=TEXT["overview_page_title"], layout="wide")
st.title(TEXT["overview_title"])

vehicles = get_all_vehicles()

if not vehicles:
    st.warning(TEXT["overview_no_vehicles"])
else:
    vehicle_data = [v.model_dump() for v in vehicles]
    df = pd.DataFrame(vehicle_data)

    df['inspection_due'] = df['documentation'].apply(lambda d: d['inspection_due'])
    df['tax_due'] = df['documentation'].apply(lambda d: d['tax_due'])

    final_columns = ['alias', 'condition', 'location', 'is_available', 'inspection_due', 'tax_due']
    df_display = df[final_columns]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "alias": st.column_config.TextColumn(TEXT["col_alias"]),
            "condition": st.column_config.TextColumn(TEXT["col_condition"]),
            "location": st.column_config.TextColumn(TEXT["col_location"]),
            "is_available": st.column_config.CheckboxColumn(TEXT["col_available"], disabled=True),
            "inspection_due": st.column_config.DateColumn(TEXT["col_inspection_due"], format="YYYY-MM-DD"),
            "tax_due": st.column_config.DateColumn(TEXT["col_tax_due"], format="YYYY-MM-DD"),
        }
    )
