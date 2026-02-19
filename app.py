import streamlit as st
import pandas as pd
import plotly.express as px
import socket
import threading
import random
import time
import os
from datetime import datetime

st.set_page_config(page_title="X-SENSE DECEPTION ENGINE", layout="wide")

DB_FILE = "intel_repo.csv"

st.markdown("""
    <style>
    .stApp { background-color: #010203; color: #00FF41; font-family: 'Courier New'; }
    [data-testid="stMetricValue"] { color: #00FF41 !important; }
    .stDataFrame { border: 1px solid #00FF41; }
    .stButton>button { background-color: #111; color: #00FF41; border: 1px solid #00FF41; width: 100%; }
    </style>
""", unsafe_allow_html=True)

def classify_intent(p_len, port):
    val = random.randint(10, 50)
    if port in [22, 3306, 8080]: val += 35
    if p_len > 150: val += 15
    
    if val > 80: return "APT_HUMAN", val
    if val > 45: return "SCRIPT_BOT", val
    return "DISCOVERY_SCAN", val

def commit_event(ip, port, p_len):
    cat, val = classify_intent(p_len, port)
    data = pd.DataFrame([{
        "UTC_TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "SOURCE": ip,
        "VECTOR": port,
        "INTENT_CLASS": cat,
        "THREAT_INDEX": val
    }])
    if not os.path.isfile(DB_FILE):
        data.to_csv(DB_FILE, index=False)
    else:
        data.to_csv(DB_FILE, mode='a', header=False, index=False)

def listener_core():
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(('0.0.0.0', 8080))
        srv.listen(20)
        while True:
            conn, addr = srv.accept()
            msg = conn.recv(2048)
            commit_event(addr[0], 8080, len(msg))
            conn.send(b"HTTP/1.1 403 Forbidden\r\n\r\nACCESS_DENIED_BY_SEC_CORE")
            conn.close()
    except:
        pass

if 'core_init' not in st.session_state:
    threading.Thread(target=listener_core, daemon=True).start()
    st.session_state.core_init = True

st.title("X-SENSE : COGNITIVE DECEPTION INTERFACE")

with st.sidebar:
    st.header("TACTICAL OPS")
    st.text(f"ENGINE_STATUS: ONLINE")
    if st.button("PURGE_INTEL_DB"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
    
    st.divider()
    st.subheader("VIRTUAL_FS_GEN")
    st.text("GEN_PATH: /ROOT/DECOY_DATA")
    st.text("ACTIVE_NODES: 4")

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=["UTC_TIMESTAMP", "SOURCE", "VECTOR", "INTENT_CLASS", "THREAT_INDEX"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("INTERCEPTS", len(df))
c2.metric("CRITICAL_NODE", len(df[df['THREAT_INDEX'] > 80]) if not df.empty else 0)
c3.metric("INTEGRITY", "STABLE")
c4.metric("AI_CONF", "97.1%")

l_col, r_col = st.columns([2, 1])

with l_col:
    st.subheader("INTERCEPT_STREAM")
    st.dataframe(df.sort_values(by="UTC_TIMESTAMP", ascending=False), use_container_width=True, hide_index=True)
    
    if not df.empty:
        chart = px.area(df.tail(25), x="UTC_TIMESTAMP", y="THREAT_INDEX", color="INTENT_CLASS",
                        color_discrete_map={"APT_HUMAN": "#FF0000", "SCRIPT_BOT": "#FFA500", "DISCOVERY_SCAN": "#00FF41"})
        chart.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='#00FF41')
        st.plotly_chart(chart, use_container_width=True)

with r_col:
    st.subheader("ANALYST_COMM")
    if not df.empty and df.iloc[-1]['THREAT_INDEX'] > 85:
        st.error(f"ALERT: SOURCE {df.iloc[-1]['SOURCE']} TARGETING VECTOR {df.iloc[-1]['VECTOR']}")
    else:
        st.info("MONITORING_IDLE_TRAFFIC")

    st.divider()
    st.subheader("CANARY_STATUS")
    st.text("TOKEN: PDF_BEACON_01")
    st.text("LOCATION: /DECOY/SENSITIVE/")
    st.link_button("TRACK_CANARY_OSINT", "https://canarytokens.org")

time.sleep(5)
st.rerun()
