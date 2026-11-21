from datetime import datetime, timedelta
import os
import sqlite3
import uuid
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- FORZAR MODO CLARO Y TEMA ROSA EN STREAMLIT ---
os.makedirs(".streamlit", exist_ok=True)
config_path = ".streamlit/config.toml"
if not os.path.exists(config_path):
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("""[theme]
base = "light"
primaryColor = "#FF69B4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#FFF5F8"
textColor = "#333333"
font = "sans serif"
""")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="DecoFiesta - Decoraciones y Eventos",
    page_icon="🌸",
    layout="wide",
)

# Estilos CSS complementarios para diseño Rosa y Blanco
st.markdown(
    """
    <style>
        .stApp {
            background-color: #FFFFFF;
            color: #333333;
        }
        
        /* Barra lateral en rosa pastel */
        [data-testid="stSidebar"] {
            background-color: #FFF5F8;
            border-right: 2px solid #FFC0CB;
        }
        
        /* Logo superior tipo banner en cada pestaña */
        .decofiesta-top-logo {
            background: linear-gradient(90deg, #FFF5F8 0%, #FFE4EC 100%);
            border: 1.5px solid #FFC0CB;
            border-left: 6px solid #FF1493;
            border-radius: 12px;
            padding: 12px 18px;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 6px rgba(255, 105, 180, 0.12);
        }
        .decofiesta-brand-title {
            color: #FF1493 !important;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 0.5px;
            margin: 0;
            line-height: 1.1;
        }
        .decofiesta-brand-sub {
            color: #9C2A6C;
            font-size: 12px;
            margin: 2px 0 0 0;
            font-weight: 500;
        }
        .decofiesta-badge {
            background-color: #FF69B4;
            color: #FFFFFF;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 999px;
        }
        
        /* Títulos */
        h1, h2, h3, h4, h5, h6 {
            color: #C71585 !important;
            font-family: 'Helvetica Neue', sans-serif;
        }
        
        /* Botones principales */
        .stButton>button {
            background-color: #FF69B4;
            color: white;
            border-radius: 8px;
            border: none;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #DB7093;
            color: white;
            box-shadow: 0 4px 8px rgba(219, 112, 147, 0.4);
        }
        
        /* Tarjetas de métricas */
        [data-testid="stMetricValue"] {
            color: #C71585 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


def render_top_logo(seccion_actual: str):
    """Muestra el logo DecoFiesta en la parte superior de cada pestaña/opción."""
    st.markdown(
        f"""
        <div class="decofiesta-top-logo">
            <div>
                <p class="decofiesta-brand-title">🌸 DecoFiesta</p>
                <p class="decofiesta-brand-sub">Decoraciones, Mobiliario y Control de Eventos</p>
            </div>
            <span class="decofiesta-badge">{seccion_actual}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- CONFIGURACIÓN BASE DE DATOS ---
DB_NAME = "ilusion_v14.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS inventario 
                         (mobiliario TEXT, tematica TEXT, stock INTEGER, costo REAL, precio REAL,
                          PRIMARY KEY (mobiliario, tematica))""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS ventas 
                         (transaccion_id TEXT, cliente TEXT, fecha TEXT, lugar TEXT, tematica TEXT, 
                          mobiliario TEXT, total REAL, anticipo REAL, estado TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS apartados 
                         (id TEXT, cliente TEXT, fecha TEXT, lugar TEXT, tematica TEXT, 
                          mobiliario TEXT, total REAL, anticipo REAL, estado TEXT)""")
        conn.commit()


def run_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


def get_df(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(query, conn, params=params)


# --- FUNCIÓN DE IMPRESIÓN ---
def ejecutar_impresion(html_content):
    unique_id = str(uuid.uuid4())[:8]
    component_script = f"""
    <div id="ticket-{unique_id}" style="display:none;">{html_content}</div>
    <script>
        (function() {{
            var content = document.getElementById('ticket-{unique_id}').innerHTML;
            var win = window.open('', 'PRINT', 'height=600,width=400');
            win.document.write('<html><head><title>Imprimir Ticket</title></head><body>' + content + '</body></html>');
            win.document.close();
            win.focus();
            win.print();
            win.close();
        }})();
    </script>
    """
    components.html(component_script, height=0)


def generar_ticket_html(
    titulo, id_doc, cliente, fecha_ev, lugar, tematica, mobiliario, total, anticipo
):
    fecha_reg = datetime.now().strftime("%d/%m/%Y %H:%M")
    restante = total - anticipo
    return f"""
    <div style="font-family: 'Courier New', monospace; width: 250px; padding: 10px; background: white; color: black; border: 1px dashed #FF69B4;">
        <center><h2 style="margin:0; color: #C71585;">DECOFIESTA</h2><p style="font-size:11px; margin:0;">Decoraciones y Eventos</p></center>
        <hr style="border-top: 1px dashed #ccc;">
        <p style="font-size:11px;"><b>{titulo}</b>: #{id_doc}<br><b>Fecha Reg:</b> {fecha_reg}</p>
        <p style="font-size:11px;">
            <b>Cliente:</b> {cliente}<br>
            <b>Fecha Evento:</b> {fecha_ev}<br>
            <b>Lugar:</b> {lugar}<br>
            <b>Temática:</b> {tematica}<br>
            <b>Mobiliario:</b> {mobiliario}
        </p>
        <hr style="border-top: 1px dashed #ccc;">
        <p style="font-size:11px;">
            <b>TOTAL:</b> ${total:,.2f}<br>
            <b>ANTICIPO:</b> ${anticipo:,.2f}<br>
            <b>RESTANTE:</b> ${restante:,.2f}
        </p>
        <center><p style="font-size:10px; margin-top:10px;">¡Gracias por su preferencia! 🌸</p></center>
    </div>
    """


# --- INICIALIZACIÓN ---
init_db()

if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "ticket_a_imprimir" not in st.session_state:
    st.session_state.ticket_a_imprimir = None

# --- NAVEGACIÓN Y LOGO EN LA ESQUINA SUPERIOR DE LA BARRA LATERAL ---
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; padding: 10px 0px 20px 0px;">
            <h2 style="color: #FF1493; margin-bottom: 0px;">🌸 DecoFiesta 🌸</h2>
            <p style="font-size: 12px; color: #666; margin-top: 0px;">Sistema de Control de Eventos</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    logo_file = st.file_uploader(
        "Subir / Cambiar Logo", type=["png", "jpg", "jpeg"], key="logo_subida"
    )
    if logo_file:
        st.image(logo_file, use_container_width=True)

    st.markdown("---")
    menu = [
        "📦 Inventario",
        "🛒 Punto de Venta",
        "📝 Apartados",
        "📊 Corte de Caja",
        "📉 Historial",
        "🛠 Admin",
        "💾 Respaldos",
    ]
    choice = st.selectbox("Seleccione opción", menu)

# Renderiza el logo superior en cada pestaña/sección activa
render_top_logo(choice)

if st.session_state.ticket_a_imprimir:
    ejecutar_impresion(st.session_state.ticket_a_imprimir)
    st.session_state.ticket_a_imprimir = None

# --- 1. INVENTARIO ---
if choice == "📦 Inventario":
    st.header("📦 Inventario de Mobiliario y Decoración")
    st.dataframe(get_df("SELECT * FROM inventario"), use_container_width=True)

# --- 2. PUNTO DE VENTA ---
elif choice == "🛒 Punto de Venta":
    st.header("🛒 Nueva Operación de Decoración")
    df_inv = get_df("SELECT * FROM inventario WHERE stock > 0")

    if not df_inv.empty:
        c1, c2 = st.columns(2)
        with c1:
            mob_sel = st.selectbox(
                "Mobiliario / Estructura", sorted(df_inv["mobiliario"].unique())
            )
            df_f = df_inv[df_inv["mobiliario"] == mob_sel]
            tem_sel = st.selectbox("Temática", sorted(df_f["tematica"].unique()))
            item = df_f[df_f["tematica"] == tem_sel].iloc[0]

            st.info(
                f"Stock disponible: {item['stock']} | Precio Sugerido: ${item['precio']:,.2f}"
            )
            cant = st.number_input("Cantidad", 1, int(item["stock"]))

            if st.button("➕ Agregar al Carrito", use_container_width=True):
                st.session_state.carrito.append({
                    "mobiliario": item["mobiliario"],
                    "tematica": item["tematica"],
                    "cantidad": cant,
                    "precio": item["precio"],
                    "subtotal": item["precio"] * cant,
                })
                st.rerun()

            if st.button(
                "🗑️ Limpiar Todo", type="secondary", use_container_width=True
            ):
                st.session_state.carrito = []
                st.rerun()

        with c2:
            if st.session_state.carrito:
                st.subheader("Resumen del Servicio")
                st.table(
                    pd.DataFrame(st.session_state.carrito)[
                        ["mobiliario", "tematica", "cantidad", "subtotal"]
                    ]
                )
                total_v = sum(i["subtotal"] for i in st.session_state.carrito)

                cli = st.text_input("Nombre del Cliente")
                fecha_ev = st.date_input(
                    "Fecha del Evento", datetime.now()
                ).strftime("%Y-%m-%d")
                lugar = st.text_input("Lugar del Evento")
                anticipo = st.number_input(
                    "Anticipo ($)", 0.0, float(total_v), float(total_v)
                )

                if st.button(
                    f"✅ Finalizar e Imprimir (${total_v:,.2f})",
                    type="primary",
                    use_container_width=True,
                ):
                    if cli and lugar:
                        t_id = str(uuid.uuid4())[:8].upper()
                        mob_str = ", ".join([
                            f"{i['cantidad']}x {i['mobiliario']}"
                            for i in st.session_state.carrito
                        ])
                        tem_str = st.session_state.carrito[0]["tematica"]

                        run_query(
                            "INSERT INTO ventas VALUES (?,?,?,?,?,?,?,?,?)",
                            (
                                t_id,
                                cli,
                                fecha_ev,
                                lugar,
                                tem_str,
                                mob_str,
                                total_v,
                                anticipo,
                                "COMPLETADA",
                            ),
                        )
                        for i in st.session_state.carrito:
                            run_query(
                                "UPDATE inventario SET stock = stock - ? WHERE mobiliario=? AND tematica=?",
                                (i["cantidad"], i["mobiliario"], i["tematica"]),
                            )

                        st.session_state.ticket_a_imprimir = (
                            generar_ticket_html(
                                "TICKET VENTA",
                                t_id,
                                cli,
                                fecha_ev,
                                lugar,
                                tem_str,
                                mob_str,
                                total_v,
                                anticipo,
                            )
                        )
                        st.session_state.carrito = []
                        st.rerun()
                    else:
                        st.error("Complete el Nombre del Cliente y el Lugar.")
    else:
        st.warning("No hay artículos con stock disponible en el inventario.")

# --- 3. APARTADOS ---
elif choice == "📝 Apartados":
    st.header("📝 Control de Apartados / Fechas")
    df_inv = get_df("SELECT * FROM inventario WHERE stock > 0")
    with st.form("ap_f"):
        cli = st.text_input("Nombre del Cliente")
        fecha_ev = st.date_input("Fecha del Evento", datetime.now()).strftime(
            "%Y-%m-%d"
        )
        lugar = st.text_input("Lugar del Evento")

        if not df_inv.empty:
            df_inv["lbl"] = (
                df_inv["mobiliario"] + " | " + df_inv["tematica"]
            )
            sel = st.selectbox("Mobiliario / Decoración", df_inv["lbl"])
        else:
            sel = st.selectbox("Mobiliario / Decoración", ["Vacío"])

        tematica_txt = st.text_input(
            "Temática Específica (Opcional)", placeholder="Ej. Barbie, Safari"
        )
        total = st.number_input("Total ($)", 0.0)
        anticipo = st.number_input("Anticipo ($)", 0.0)

        if st.form_submit_button("Guardar Apartado"):
            if not df_inv.empty and cli:
                r = df_inv[df_inv["lbl"] == sel].iloc[0]
                ap_id = "AP-" + str(uuid.uuid4())[:4].upper()
                tem_final = (
                    tematica_txt if tematica_txt.strip() else r["tematica"]
                )

                run_query(
                    "INSERT INTO apartados VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        ap_id,
                        cli,
                        fecha_ev,
                        lugar,
                        tem_final,
                        r["mobiliario"],
                        total,
                        anticipo,
                        "ACTIVO",
                    ),
                )
                run_query(
                    "UPDATE inventario SET stock = stock - 1 WHERE mobiliario=? AND tematica=?",
                    (r["mobiliario"], r["tematica"]),
                )

                st.session_state.ticket_a_imprimir = generar_ticket_html(
                    "VALE APARTADO",
                    ap_id,
                    cli,
                    fecha_ev,
                    lugar,
                    tem_final,
                    r["mobiliario"],
                    total,
                    anticipo,
                )
                st.rerun()
            else:
                st.error("Ingrese el cliente y asegúrese de tener inventario.")

# --- 4. CORTE DE CAJA ---
elif choice == "📊 Corte de Caja":
    st.header("📊 Corte de Caja y Finanzas")
    periodo = st.radio(
        "Seleccione Periodo de Corte:",
        ["Hoy", "Esta Semana", "Este Mes"],
        horizontal=True,
    )

    hoy = datetime.now()
    if periodo == "Hoy":
        fecha_inicio = hoy.strftime("%Y-%m-%d")
    elif periodo == "Esta Semana":
        fecha_inicio = (hoy - timedelta(days=hoy.weekday())).strftime(
            "%Y-%m-%d"
        )
    else:
        fecha_inicio = hoy.strftime("%Y-%m-01")

    query_corte = """
        SELECT v.*, i.costo 
        FROM ventas v 
        LEFT JOIN inventario i ON v.mobiliario = i.mobiliario AND v.tematica = i.tematica
        WHERE v.fecha >= ? AND v.estado = 'COMPLETADA'
    """
    df_corte = get_df(query_corte, (fecha_inicio,))

    if not df_corte.empty:
        total_ventas = df_corte["total"].sum()
        total_anticipos = df_corte["anticipo"].sum()
        total_costos = df_corte["costo"].fillna(0).sum()
        utilidad = total_anticipos - total_costos

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Contratado", f"${total_ventas:,.2f}")
        m2.metric("Total Anticipos (Cobrado)", f"${total_anticipos:,.2f}")
        m3.metric("Utilidad / Neto Recibido", f"${utilidad:,.2f}")

        st.subheader("Detalle de Ventas en el Periodo")
        st.dataframe(
            df_corte[[
                "transaccion_id",
                "fecha",
                "cliente",
                "lugar",
                "tematica",
                "mobiliario",
                "total",
                "anticipo",
            ]],
            use_container_width=True,
        )
    else:
        st.info(f"No hay ventas registradas desde el {fecha_inicio}")

# --- 5. HISTORIAL ---
elif choice == "📉 Historial":
    st.header("📉 Historial de Operaciones")
    st.subheader("Ventas")
    st.dataframe(get_df("SELECT * FROM ventas"), use_container_width=True)
    st.subheader("Apartados")
    st.dataframe(get_df("SELECT * FROM apartados"), use_container_width=True)

# --- 6. ADMIN ---
elif choice == "🛠 Admin":
    st.header("🛠 Panel de Administración - Inventario")
    with st.form("adm"):
        c1, c2, c3, c4, c5 = st.columns(5)
        mob = c1.text_input("Mobiliario")
        tem = c2.text_input("Temática")
        s = c3.number_input("Stock", 0)
        pc = c4.number_input("Costo", 0.0)
        pv = c5.number_input("Precio Sugerido", 0.0)
        if st.form_submit_button("Guardar en Inventario"):
            if mob and tem:
                run_query(
                    "INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?)",
                    (mob, tem, s, pc, pv),
                )
                st.success("Guardado en inventario exitosamente.")
                st.rerun()
            else:
                st.error("Ingrese Mobiliario y Temática.")

# --- 7. RESPALDOS ---
elif choice == "💾 Respaldos":
    st.header("💾 Gestión de Respaldos de Base de Datos")
    if os.path.exists(DB_NAME):
        with open(DB_NAME, "rb") as f:
            st.download_button(
                "📥 Descargar Base de Datos (.db)",
                f,
                f"Backup_DecoFiesta_{datetime.now().strftime('%Y%m%d')}.db",
            )

    file_up = st.file_uploader("Restaurar Base de Datos", type=["db"])
    if file_up and st.button("🚀 Restaurar"):
        with open(DB_NAME, "wb") as f:
            f.write(file_up.getbuffer())
        st.success("Base de datos restaurada con éxito.")
        st.rerun()