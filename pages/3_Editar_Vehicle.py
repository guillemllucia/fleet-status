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

        new_alias = st.text_input(TEXT["add_alias_label"], value=selected_vehicle.alias)
        location = st.text_input(TEXT["add_location_label"], value=selected_vehicle.location)

        condition_options = [c.value for c in VehicleCondition]
        condition_index = condition_options.index(selected_vehicle.condition)
        condition = st.selectbox(TEXT["add_condition_label"], options=condition_options, index=condition_index)

        inspection_due = st.date_input(TEXT["add_inspection_label"], value=selected_vehicle.documentation.inspection_due.date())
        tax_due = st.date_input(TEXT["add_tax_label"], value=selected_vehicle.documentation.tax_due.date())

        # --- DYNAMIC FORM FOR NON-RUNNING DETAILS ---
        if condition == "No operatiu":
            st.warning(TEXT["add_non_running_warning"])

            # Pre-fill with existing data if it exists, otherwise use defaults
            current_details = selected_vehicle.non_running_details
            explanation = st.text_area(TEXT["add_explanation_label"], value=current_details.explanation if current_details else "")
            budget = st.number_input(TEXT["add_budget_label"], min_value=0.0, step=50.0, value=current_details.estimated_budget if current_details else 0.0)
            eta = st.date_input(TEXT["add_eta_label"], value=current_details.eta.date() if current_details else datetime.today().date())
        # --- END OF DYNAMIC FORM ---

        submitted = st.form_submit_button(TEXT["manage_save_button"])

        if submitted:
            # Base dictionary of fields that are always updated
            updates = {
                "alias": new_alias,
                "location": location,
                "condition": condition,
                "documentation.inspection_due": datetime.combine(inspection_due, datetime.min.time()),
                "documentation.tax_due": datetime.combine(tax_due, datetime.min.time()),
            }

            # Add or remove the non_running_details based on the selected condition
            if condition == "No operatiu":
                updates["non_running_details"] = {
                    "explanation": explanation,
                    "estimated_budget": budget,
                    "eta": datetime.combine(eta, datetime.min.time())
                }
            else:
                # If the vehicle is now running, remove the old repair details
                updates["non_running_details"] = None

            success = update_vehicle(str(selected_vehicle.id), updates)

            if success:
                st.success(TEXT["manage_update_success"])
                st.rerun()
            else:
                st.error(TEXT["manage_update_fail"])

    # --- DELETE SECTION ---
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
