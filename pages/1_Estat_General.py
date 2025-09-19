import streamlit as st
from src.database import get_all_vehicles
from src.i18n import TEXT

st.set_page_config(page_title=TEXT["overview_page_title"], layout="wide")
st.title(TEXT["overview_title"])

vehicles = get_all_vehicles()

if not vehicles:
    st.warning(TEXT["overview_no_vehicles"])
else:
    num_columns = 4
    cols = st.columns(num_columns)

    for index, vehicle in enumerate(vehicles):
        col = cols[index % num_columns]

        with col.container(border=True):
            if vehicle.photo_url:
                st.image(vehicle.photo_url, use_container_width=True)
            else:
                # Update placeholder to match the 800x600 (4:3) ratio
                st.image("https://placehold.co/800x600/222/FFF?text=No+Foto", use_container_width=True)

            st.subheader(vehicle.alias)

            # Determine status and display it
            if vehicle.is_available:
                status_text = "Disponible"
                status_color = "green"
                status_icon = "✅"
                st.markdown(
                    f"<h4>{status_icon} <span style='color:{status_color};'>{status_text}</span></h4>",
                    unsafe_allow_html=True
                )
            else:
                status_text = "No disponible"
                status_color = "red"
                status_icon = "❌"
                st.markdown(
                    f"<h4>{status_icon} <span style='color:{status_color};'>{status_text}</span></h4>",
                    unsafe_allow_html=True
                )
                # If not available, show the reason why
                if vehicle.condition == "No operatiu" and vehicle.non_running_details:
                    st.info(f"**Motiu:** {vehicle.non_running_details.explanation}")

            # Display other details in an expander to keep the UI clean
            with st.expander("Més detalls"):
                st.write(f"**Ubicació:** {vehicle.location}")
                st.write(f"**Caducitat ITV:** {vehicle.documentation.inspection_due.strftime('%Y-%m-%d')}")
                st.write(f"**Caducitat Impost:** {vehicle.documentation.tax_due.strftime('%Y-%m-%d')}")
                if vehicle.condition == "No operatiu" and vehicle.non_running_details:
                    st.write(f"**Pressupost:** {vehicle.non_running_details.estimated_budget}€")
                    st.write(f"**ETA:** {vehicle.non_running_details.eta.strftime('%Y-%m-%d')}")
