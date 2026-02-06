import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json

# Setting ui
st.set_page_config(
    page_title="SalesGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS biar lebih clean
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('creditcard.csv')
        return df.sample(100) # ambil dikit buat sampling biar enteng
    except FileNotFoundError:
        return None

df_sample = load_data()

# sidebar control
st.sidebar.header("🔧 Control Panel")
st.sidebar.markdown("---")

if st.sidebar.button("🎲 Generate Random Transaction"):
    if df_sample is not None:
        st.session_state['tx_data'] = df_sample.sample(1).iloc[0]
        st.sidebar.success("Data ready!")
    else:
        st.sidebar.error("File creditcard.csv ilang!")

if st.sidebar.button("⚠️ Force Fraud Transaction (Demo)"):
    try:
        # Cari data yang emang labelnya Fraud (Class 1) buat testing
        df_full = pd.read_csv('creditcard.csv')
        st.session_state['tx_data'] = df_full[df_full['Class'] == 1].sample(1).iloc[0]
        st.sidebar.warning("Data FRAUD ke-load. Cek analisa sekarang.")
    except Exception as e:
        st.sidebar.error(f"Gagal load data fraud: {e}")

# main ui
st.title("🛡️ SalesGuard: AI Fraud Detection System")
st.markdown("Deteksi anomali transaksi via **Random Forest**.")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Detail Transaksi")
    
    if 'tx_data' in st.session_state:
        tx = st.session_state['tx_data']
        st.info(f"""
        **Amount:** ${tx['Amount']}
        \n**Fitur V1:** {tx['V1']:.4f}
        \n**Fitur V2:** {tx['V2']:.4f}
        \n**Fitur V3:** {tx['V3']:.4f}
        \n*(V4-V28 hidden)*
        """)
    else:
        st.warning("Generate data dulu di sidebar.")

with col2:
    st.subheader("2. Hasil Analisa Real-time")
    
    if 'tx_data' in st.session_state:
        if st.button("🔍 Cek Analisa AI", type="primary"):
            tx = st.session_state['tx_data']
            
            # Buang 'Class' & 'Time' karena model cuma minta 29 fitur (V1-V28 + Amount)
            tx_input = tx.drop(['Class', 'Time'], errors='ignore')
            features = tx_input.tolist()
            
            try:
                # Hit ke FastAPI
                response = requests.post("http://127.0.0.1:8000/predict", json={"features": features})
                
                if response.status_code == 200:
                    res = response.json()
                    is_fraud = res['prediction'] == "Fraud"
                    
                    if is_fraud:
                        st.error("🚨 PERINGATAN: TRANSAKSI MENCURIGAKAN!")
                    else:
                        st.success("✅ Transaksi Aman")

                    st.metric(
                        label="Fraud Probability", 
                        value=f"{res['probability']:.2f}%", 
                        delta="High Risk" if is_fraud else "Safe",
                        delta_color="inverse" if is_fraud else "normal"
                    )
                    
                    # Plotting distribusi V1-V28 (Skip 'Amount' karena skalanya beda sendiri)
                    st.subheader("Pola Fitur (V1-V28)")
                    df_chart = pd.DataFrame({
                        'Fitur': tx_input.index,
                        'Nilai': tx_input.values
                    }).query("Fitur.str.startswith('V')")
                    
                    fig = px.bar(df_chart, x='Fitur', y='Nilai', 
                                 color_discrete_sequence=['red' if is_fraud else 'blue'])
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.error(f"API Error: {response.status_code}")
            
            except Exception as e:
                st.error(f"Koneksi backend gagal. Cek uvicorn!")