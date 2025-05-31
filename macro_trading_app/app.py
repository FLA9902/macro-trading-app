
[Mobile-optimized code is prepared in the backend update. Placeholder for actual content.]



from email_utils import send_email_with_results

st.subheader("📧 Email Results")

api_key = st.secrets.get("RESEND_API_KEY", "")
sender_email = st.secrets.get("SENDER_EMAIL", "")
recipient_email = st.text_input("Enter your email to receive the results", key="email")

if recipient_email and st.button("📬 Send Results via Email"):
    if not api_key or not sender_email:
        st.error("❌ Email sending is not configured properly.")
    elif "results" not in st.session_state or not st.session_state["results"]:
        st.error("⚠️ No screening results available to send.")
    else:
        summary_text = "\n".join(
            [f"{r['Ticker']}: {'✅' if r['Fits Strategy'] else '❌'}" for r in st.session_state["results"]]
        )
        df_results = pd.DataFrame(st.session_state["results"])
        csv = df_results.to_csv(index=False).encode('utf-8')
        status, response = send_email_with_results(api_key, recipient_email, sender_email, csv, summary_text)
        if status == 200:
            st.success("✅ Email sent successfully!")
        else:
            st.error(f"❌ Failed to send email: {response}")
