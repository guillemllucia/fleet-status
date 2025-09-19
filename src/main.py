import os
import streamlit as st
import pandas as pd
from datetime import date, datetime
from dotenv import load_dotenv

# Import database functions and models
from src.database import get_all_vehicles, add_vehicle
from src.models import Vehicle, VehicleCondition, Documentation, NonRunningDetails

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(layout="wide")

    # Get config from environment variables
    app_title = os.getenv("APP_TITLE", "Fleet Status")
    st.title(app_title)

    # --- Data Entry Form ---
    with st.expander("➕ Add New Vehicle", expanded=False):
        with st.form("new_vehicle_form"):
            st.subheader("Vehicle Details")

            # Use columns for a cleaner layout
            col1, col2 = st.columns(2)

            with col1:
                alias = st.text_input("Alias (e.g., Ford Mustang 1968)", key="alias")
                location = st.text_input("Current Location", key="location")
                photo_url = st.text_input("Photo URL (Optional)", key="photo_url")

            with col2:
                condition = st.selectbox(
                    "Condition",
                    options=[c.value for c in VehicleCondition],
                    key="condition"
                )
                inspection_due = st.date_input("Inspection Due Date", value=date.today(), key="inspection_due")
                tax_due = st.date_input("Tax Due Date", value=date.today(), key="tax_due")

            # Conditional form for non-running vehicles
            non_running_details_data = None
            if condition == VehicleCondition.NON_RUNNING.value:
                st.warning("Please provide details for the non-running vehicle:")
                explanation = st.text_area("What needs to be fixed?", key="explanation")
                estimated_budget = st.number_input("Estimated Budget (€)", min_value=0.0, step=50.0, key="budget")
                eta = st.date_input("Estimated Completion Date (ETA)", value=date.today(), key="eta")
                non_running_details_data = {
                    "explanation": explanation,
                    "estimated_budget": estimated_budget,
                    "eta": eta
                }

            submitted = st.form_submit_button("Add Vehicle")

            if submitted:
                if not alias or not location:
                    st.error("Alias and Location are required fields.")
                else:
                    # --- THIS IS THE SECTION TO CHANGE ---
                    # Convert date objects to datetime objects
                    inspection_datetime = datetime.combine(inspection_due, datetime.min.time())
                    tax_datetime = datetime.combine(tax_due, datetime.min.time())

                    # Create the Pydantic models from form data
                    doc_model = Documentation(inspection_due=inspection_datetime, tax_due=tax_datetime)

                    nr_details_model = None
                    if non_running_details_data:
                        eta_datetime = datetime.combine(non_running_details_data["eta"], datetime.min.time())
                        nr_details_model = NonRunningDetails(
                            explanation=non_running_details_data["explanation"],
                            estimated_budget=non_running_details_data["estimated_budget"],
                            eta=eta_datetime
                        )
                    # --- END OF SECTION TO CHANGE ---

                    new_vehicle = Vehicle(
                        alias=alias,
                        photo_url=photo_url or None,
                        condition=condition,
                        non_running_details=nr_details_model,
                        documentation=doc_model,
                        location=location
                    )

                    add_vehicle(new_vehicle)
                    st.success(f"Vehicle '{alias}' added successfully!")
                    st.rerun() # Rerun the app to refresh the vehicle list

    st.header("Vehicle Fleet Overview")

    # --- Data Display Table ---
    vehicles = get_all_vehicles()

    if not vehicles:
        st.warning("No vehicles found in the database. Add a vehicle using the form above to get started.")
        return

    # Convert Pydantic objects to a DataFrame for display
    vehicle_data = [v.model_dump() for v in vehicles]
    df = pd.DataFrame(vehicle_data)

    # Extract nested documentation data for display
    df['inspection_due'] = df['documentation'].apply(lambda d: d['inspection_due'])
    df['tax_due'] = df['documentation'].apply(lambda d: d['tax_due'])

    # Final column selection and ordering
    final_columns = ['alias', 'condition', 'location', 'is_available', 'inspection_due', 'tax_due']
    df_display = df[final_columns]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "is_available": st.column_config.CheckboxColumn("Available?", disabled=True),
            "inspection_due": st.column_config.DateColumn("Inspection Due", format="YYYY-MM-DD"),
            "tax_due": st.column_config.DateColumn("Tax Due", format="YYYY-MM-DD"),
        }
    )

if __name__ == "__main__":
    main()
