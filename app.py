import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="Kiran T. | SRE Incident Analyzer", 
    page_icon="🛠️", 
    layout="wide"
)

# 2. Setup Groq Client
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ GROQ_API_KEY missing in Streamlit Secrets.")
    st.stop()

# 3. Sidebar: SRE Profile & CSV Loader
with st.sidebar:
    try:
        st.image("profile.jpg", use_container_width=True)
    except:
        st.info("📷 profile.jpg not found.")
    
    st.title("Kiran T.")
    st.write("🚀 **SRE Incident Analysis Engine**")
    st.divider()

    # Model Settings
    st.subheader("⚙️ AI Brain Settings")
    model_id = st.selectbox("Select Model:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    st.divider()
    st.caption("Upload 'incidents.csv' to GitHub to analyze your historical data.")

# 4. Data Loading Logic (CSV)
@st.cache_data
def load_incident_data():
    try:
        df = pd.read_csv("incidents.csv")
        return df
    except FileNotFoundError:
        return None

incident_df = load_incident_data()

# 5. Main Layout: [3 Columns for Chat, 1 Column for GIFs]
col_chat, col_visuals = st.columns([3, 1], gap="large")

# --- LEFT COLUMN: Incident Chat & Data ---
with col_chat:
    st.header("🔍 Step-by-Step Incident Analysis")
    
    if incident_df is not None:
        with st.expander("📊 View Raw Incident Logs"):
            st.dataframe(incident_df, use_container_width=True)
        
        context_data = incident_df.to_string() # Convert CSV to text for AI context
    else:
        st.warning("⚠️ 'incidents.csv' not found in repository. Please upload it to use analysis features.")
        context_data = "No incident data available."

    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Helper for streaming
    def generate_groq_response(response):
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # Interaction
    if prompt := st.chat_input("Ask for a step-by-step RCA of an incident (e.g., 'Analyze the database outage')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # SRE Analysis System Prompt
                sys_prompt = (
                    f"You are a Senior SRE. Use the following incident logs: {context_data}. "
                    "When asked to analyze an incident, provide a step-by-step process: "
                    "1. Detection & Alerting, 2. Immediate Triage, 3. Root Cause Analysis (RCA), "
                    "4. Resolution Steps, and 5. Post-Mortem Recommendations."
                )

                raw_stream = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    stream=True
                )
                full_res = st.write_stream(generate_groq_response(raw_stream))
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error(f"Inference Error: {e}")

# --- RIGHT COLUMN: SRE & AWS GIFs ---
with col_visuals:
    st.write("### Monitoring Status")
    
    # SRE GIF
    try:
        st.image("sre.gif", caption="Site Reliability Engineering", use_container_width=True)
    except:
        st.caption("⚠️ sre.gif missing")
        
    st.divider()
    
    # AWS GIF
    try:
        st.image("aws.gif", caption="AWS Infrastructure", use_container_width=True)
    except:
        st.caption("⚠️ aws.gif missing")
