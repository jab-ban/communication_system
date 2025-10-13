import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
from itertools import cycle

# ---------- Page Config ----------
st.set_page_config(page_title="📧 Email Sender App", page_icon="📨", layout="centered")

# ---------- Custom CSS for styling ----------
st.markdown("""
    <style>
        .main {
            background-color: #f9f9fb;
            padding: 2rem;
            border-radius: 15px;
        }
        h1 {
            color: #4B8BBE;
            text-align: center;
            font-family: 'Helvetica Neue', sans-serif;
        }
        .stTextInput, .stTextArea, .stSlider, .stFileUploader {
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 0 5px rgba(0,0,0,0.05);
        }
        .stButton > button {
            background-color: #4B8BBE;
            color: white;
            border-radius: 10px;
            font-weight: bold;
            padding: 0.6rem 1.2rem;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #357ABD;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.title("📨 Email Sender App")
st.markdown("### Send personalized emails easily using multiple sender accounts.")

st.markdown("---")

# ---------- File Uploads ----------
col1, col2 = st.columns(2)
with col1:
    uploaded_file_recievers = st.file_uploader("📁 Upload Receivers CSV", type="csv", help="File must contain 'name' and 'email' columns.")
with col2:
    uploaded_file_senders = st.file_uploader("📤 Upload Senders CSV", type="csv", help="File must contain 'email' and 'app_password' columns.")

st.markdown("---")

# ---------- Settings ----------
st.subheader("⚙️ Email Settings")

subject = st.text_input("📌 Email Subject", "Test Email")

body_template = st.text_area(
    "💌 Email Body",
    value="Hello \nThis is a test email from my project!"
)

delay = st.slider("⏳ Delay between emails (seconds)", 1, 10, 2)
# ---------- Start sending ----------
if uploaded_file_recievers is not None and uploaded_file_senders is not None:
    recievers_df = pd.read_csv(uploaded_file_recievers)
    senders_df = pd.read_csv(uploaded_file_senders)

    st.success(f"✅ Receivers loaded successfully: **{len(recievers_df)}**")
    st.success(f"✅ Senders loaded successfully: **{len(senders_df)}**")
    if "dept" in recievers_df.columns:
        departments = sorted(recievers_df["dept"].dropna().unique().tolist())
        departments.insert(0, "All Departments")  

        selected_dept = st.selectbox("🏢 Choose Department", departments)

       
        if selected_dept == "All Departments":
            filtered_df = recievers_df
            st.info(f"📋 Sending to ALL departments ({len(filtered_df)} total).")
        else:
            filtered_df = recievers_df[recievers_df["dept"] == selected_dept]
            st.info(f"📋 {len(filtered_df)} receiver(s) found in {selected_dept} department.")
    else:
        st.error("❌ 'dept' column not found in your CSV!")
        filtered_df = recievers_df 

    senders_cycle = cycle(senders_df.to_dict(orient="records"))

    st.markdown("---")
    st.subheader("🚀 Ready to Send")

    if st.button("📨 Send Emails Now"):
        progress_bar = st.progress(0)
        total = len(recievers_df)
        sent_count = 0

        for index, row in recievers_df.iterrows():
            receiver = row["email"]
            name = row["name"]

            # Next sender in the cycle
            sender_data = next(senders_cycle)
            sender_email = sender_data["email"]
            app_password = sender_data["app_password"]

            message = body_template.format(name=name)

            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = receiver

            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                server.quit()
                st.success(f"✅ Sent to **{receiver}** from **{sender_email}**")
                sent_count += 1
            except Exception as e:
                st.error(f"❌ Failed for {receiver}: {e}")

            time.sleep(delay)
            progress_bar.progress((index + 1) / total)

        

else:
    st.info("📥 Please upload both CSV files to start.")






