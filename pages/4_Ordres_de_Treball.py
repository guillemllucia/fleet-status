import streamlit as st
from bson import ObjectId
from datetime import datetime, date
from src.database import get_all_vehicles, add_work_order, get_work_orders_for_vehicle
from src.models import WorkOrder
from src.i18n import TEXT

st.set_page_config(page_title="Ordres de Treball", layout="wide")
st.title("Gestió d'Ordres de Treball 🛠️")

vehicles = get_all_vehicles()

if not vehicles:
    st.warning(TEXT["manage_no_vehicles"])
else:
    vehicle_map = {v.alias: v for v in vehicles}
    selected_alias = st.selectbox(
        TEXT["manage_select_vehicle"],
        options=vehicle_map.keys()
    )
    selected_vehicle = vehicle_map[selected_alias]

    st.header(f"Ordres per a: {selected_vehicle.alias}")

    # --- Section to Add a New Work Order ---
    with st.expander("➕ Afegeix una Ordre de Treball Nova"):

        # --- THIS IS THE KEY CHANGE ---
        # Move the checkbox outside the form to allow the callback
        is_tbd = st.checkbox("ETA per determinar (TBD)")

        with st.form("new_work_order_form", clear_on_submit=True):
            title = st.text_input("Títol (p. ex., 'Canvi d'oli i filtres')")
            description = st.text_area("Descripció de les tasques")
            cost = st.number_input("Cost Estimat (€)", min_value=0.0, step=25.0)

            # The date input is now inside the form, but disabled by the checkbox outside
            eta_date = st.date_input(
                "Data Estimada de Finalització (ETA)",
                value=date.today(),
                disabled=is_tbd
            )

            submitted = st.form_submit_button("Crea Ordre de Treball")

            if submitted:
                if not title:
                    st.error("El títol és obligatori.")
                else:
                    new_order = WorkOrder(
                        vehicle_id=selected_vehicle.id,
                        title=title,
                        description=description,
                        cost=cost,
                        start_date=datetime.now(),
                        eta=None if is_tbd else datetime.combine(eta_date, datetime.min.time()),
                        eta_is_tbd=is_tbd
                    )
                    add_work_order(new_order)
                    st.success(f"S'ha creat l'ordre de treball '{title}'.")
                    st.rerun()

    # --- Section to Display Existing Work Orders ---
    st.divider()
    st.subheader("Historial d'Ordres de Treball")
    work_orders = get_work_orders_for_vehicle(str(selected_vehicle.id))

    if not work_orders:
        st.info("Aquest vehicle no té cap ordre de treball.")
    else:
        for order in sorted(work_orders, key=lambda o: o.start_date, reverse=True):
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{order.title}**")
                    st.caption(f"Iniciada: {order.start_date.strftime('%Y-%m-%d')}")
                    st.write(order.description)
                with col2:
                    if order.eta_is_tbd:
                        st.metric("ETA", "TBD")
                    elif order.eta:
                        st.metric("ETA", order.eta.strftime('%Y-%m-%d'))
                with col3:
                    st.metric("Cost", f"{order.cost} €")
