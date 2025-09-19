import streamlit as st
from src.database import get_all_vehicles, update_vehicle, delete_vehicle
from src.models import VehicleCondition
from datetime import datetime
from src.i18n import TEXT

st.set_page_config(page_title=TEXT["manage_page_title"], layout="wide")
st.title(TEXT["manage_title"])

vehicles = get_all_vehicles()

if not vehicles:
    st.warning(TEXT["manage_no_vehicles"])
else:
    vehicle_map = {v.alias: v for v in vehicles}
    alias_to_edit = st.selectbox(TEXT["manage_select_vehicle"], options=vehicle_map.keys())

    selected_vehicle = vehicle_map[alias_to_edit]

    with st.form("edit_vehicle_form"):
        st.subheader(TEXT["manage_editing_subheader"].format(alias=selected_vehicle.alias))

        location = st.text_input(TEXT["add_location_label"], value=selected_vehicle.location)
        condition_options = [c.value for c in VehicleCondition]
        condition_index = condition_options.index(selected_vehicle.condition)
        condition = st.selectbox(TEXT["add_condition_label"], options=condition_options, index=condition_index)

        inspection_due = st.date_input(TEXT["add_inspection_label"], value=selected_vehicle.documentation.inspection_due.date())
        tax_due = st.date_input(TEXT["add_tax_label"], value=selected_vehicle.documentation.tax_due.date())

        submitted = st.form_submit_button(TEXT["manage_save_button"])

        if submitted:
            updates = {
                "location": location,
                "condition": condition,
                "documentation.inspection_due": datetime.combine(inspection_due, datetime.min.time()),
                "documentation.tax_due": datetime.combine(tax_due, datetime.min.time()),
            }
            success = update_vehicle(str(selected_vehicle.id), updates)
            if success:
                st.success(TEXT["manage_update_success"])
            else:
                st.error(TEXT["manage_update_fail"])

    st.divider()
    with st.expander(TEXT["danger_zone_title"]):
        st.subheader(TEXT["delete_subheader"])
        st.warning(TEXT["delete_warning"].format(alias=selected_vehicle.alias))

        confirm_delete = st.checkbox(TEXT["delete_confirm_checkbox"])

        if confirm_delete:
            if st.button(TEXT["delete_button"], type="primary"):
                success = delete_vehicle(str(selected_vehicle.id))
                if success:
                    st.success(TEXT["delete_success"].format(alias=selected_vehicle.alias))
                    st.rerun()
                else:
                    st.error(TEXT["delete_fail"])
