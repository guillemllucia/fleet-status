import streamlit as st
from datetime import date, datetime
from src.database import add_vehicle
from src.models import Vehicle, VehicleCondition, Documentation, NonRunningDetails
from src.i18n import TEXT

st.set_page_config(page_title=TEXT["add_page_title"], layout="wide")
st.title(TEXT["add_title"])

with st.form("new_vehicle_form"):
    st.subheader(TEXT["add_form_subheader"])

    col1, col2 = st.columns(2)

    with col1:
        alias = st.text_input(TEXT["add_alias_label"])
        location = st.text_input(TEXT["add_location_label"])
        photo_url = st.text_input(TEXT["add_photo_label"])

    with col2:
        condition = st.selectbox(
            TEXT["add_condition_label"],
            options=[c.value for c in VehicleCondition]
        )
        inspection_due = st.date_input(TEXT["add_inspection_label"], value=date.today())
        tax_due = st.date_input(TEXT["add_tax_label"], value=date.today())

    non_running_details_data = None
    if condition == VehicleCondition.NON_RUNNING.value:
        st.warning(TEXT["add_non_running_warning"])
        explanation = st.text_area(TEXT["add_explanation_label"])
        estimated_budget = st.number_input(TEXT["add_budget_label"], min_value=0.0, step=50.0)
        eta = st.date_input(TEXT["add_eta_label"], value=date.today())
        non_running_details_data = {
            "explanation": explanation,
            "estimated_budget": estimated_budget,
            "eta": eta
        }

    submitted = st.form_submit_button(TEXT["add_submit_button"])

    if submitted:
        if not alias or not location:
            st.error(TEXT["add_error_required"])
        else:
            inspection_datetime = datetime.combine(inspection_due, datetime.min.time())
            tax_datetime = datetime.combine(tax_due, datetime.min.time())
            doc_model = Documentation(inspection_due=inspection_datetime, tax_due=tax_datetime)

            nr_details_model = None
            if non_running_details_data:
                eta_datetime = datetime.combine(non_running_details_data["eta"], datetime.min.time())
                nr_details_model = NonRunningDetails(
                    explanation=non_running_details_data["explanation"],
                    estimated_budget=non_running_details_data["estimated_budget"],
                    eta=eta_datetime
                )

            new_vehicle = Vehicle(
                alias=alias,
                photo_url=photo_url or None,
                condition=condition,
                non_running_details=nr_details_model,
                documentation=doc_model,
                location=location
            )

            add_vehicle(new_vehicle)
            st.success(TEXT["add_success_message"].format(alias=alias))
