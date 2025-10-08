import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
from itertools import cycle
st.title("📧 Email Sender App")
uploaded_file_recievers = st.file_uploader("Upload your CSV file (must have 'name' and 'email' columns)", type="csv")
uploaded_file_senders=st.file_uploader("Upload your CSV file (must have 'email' and 'app_password'columns)", type="csv")
delay = st.slider("Delay between emails (seconds)", 1, 10, 2)
subject=st.text_input("Email Subject", "Test Email")
body_template = st.text_area("Email Body", value="Hello {name},\nThis is a test email from my project!")
if uploaded_file_recievers is not None and uploaded_file_senders is not None:
    recievers_df = pd.read_csv(uploaded_file_recievers)
    senders_df=pd.read_csv(uploaded_file_senders)
    st.write("✅ recievers loaded successfully",len(recievers_df))
    st.write("✅ senders loaded successfully",len(senders_df))
    
    senders_cycle = cycle(senders_df.to_dict(orient="records"))
    if st.button("Send Emails"):
        
            for index, row in recievers_df.iterrows():
                receiver = row["email"]
                name = row["name"]

                # the next sender in the cycle
                sender_data=next(senders_cycle)
                sender_email=sender_data["email"]
                app_password=sender_data["app_password"]
                message = body_template.format(name=name)#نص الرسالة

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
                 st.success(f"✅ Sent to {receiver} from {sender_email}")
                except Exception as e:
                 st.error(f"❌ Failed for {receiver}: {e}")

                time.sleep(delay)