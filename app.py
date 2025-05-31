try:
    import streamlit as st
    import pdfplumber
    import pandas as pd
    import matplotlib.pyplot as plt
    import re
    import openai

    st.set_page_config(page_title="Brokerage Dashboard", layout="wide")

    st.title("📊 Brokerage Statement Dashboard")
    st.markdown("Upload a Fidelity statement PDF and view a clean summary of your portfolio.")

    openai_api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
    uploaded_file = st.file_uploader("Upload your brokerage statement (PDF)", type="pdf")

    if uploaded_file:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])

        match = re.search(r"Your Net Portfolio Value: \$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", text)
        portfolio_value = match.group(1) if match else "Not found"

        holdings_data = []
        possible_holdings = re.findall(r"(?m)^(.+?)\s+\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(\d+)%$", text)
        for name, value_str, percent_str in possible_holdings:
            try:
                cleaned_name = name.strip()
                if re.search(r"(?i)total|balance details|summary", cleaned_name):
                    continue
                value = float(value_str.replace(",", ""))
                percent = int(percent_str)
                if value > 0 and percent > 0:
                    holdings_data.append({"Holding": cleaned_name, "Value ($)": value, "% of Portfolio": percent})
            except:
                continue

        df_holdings = pd.DataFrame(holdings_data)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("💼 Portfolio Overview")
            st.metric("Net Portfolio Value", f"${portfolio_value}")

            if not df_holdings.empty:
                df_top = df_holdings.sort_values(by="Value ($)", ascending=False).head(10)
                st.subheader("📋 Top 10 Holdings")
                st.dataframe(df_top, use_container_width=True)
            else:
                st.warning("No holdings found. Please upload a properly formatted statement.")

        with col2:
            if not df_holdings.empty:
                st.subheader("🧩 Allocation Breakdown")
                fig, ax = plt.subplots()
                ax.pie(df_top["% of Portfolio"], labels=df_top["Holding"], autopct='%1.1f%%', startangle=140)
                ax.axis('equal')
                st.pyplot(fig)

        if not df_holdings.empty:
            st.subheader("📈 Holdings Bar Chart")
            fig2, ax2 = plt.subplots()
            ax2.barh(df_top["Holding"], df_top["Value ($)"])
            ax2.set_xlabel("Value ($)")
            ax2.set_title("Top Holdings")
            st.pyplot(fig2)

        if openai_api_key and not df_holdings.empty:
            st.subheader("📝 AI Portfolio Summary")
            openai.api_key = openai_api_key
            try:
                prompt = """Summarize this investment portfolio in a professional, clear format for a client:\n\n""" + df_top.to_string(index=False)
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a financial analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )
                summary = response['choices'][0]['message']['content']
                st.write(summary)
            except Exception as e:
                st.error(f"Failed to generate AI summary: {e}")

        st.markdown("---")
        st.info("Prototype view only. Upload Fidelity statements for best results.")

except ModuleNotFoundError as e:
    print("\nERROR: Missing module. Please ensure all dependencies are installed.")
    print("\nError detail:", str(e))
    print("\nTo fix, run:")
    print("pip install streamlit pdfplumber matplotlib pandas openai")

except Exception as e:
    print("\nAn unexpected error occurred:", str(e))
