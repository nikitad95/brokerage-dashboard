try:
    import streamlit as st
    import pdfplumber
    import pandas as pd
    import matplotlib.pyplot as plt
    import re
    import openai

    st.set_page_config(page_title="Brokerage Dashboard", layout="wide")

    st.title("📊 Brokerage Statement Dashboard")
    st.markdown("Upload a Fidelity statement PDF and view a clear, visual summary of your portfolio.")

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
                value = float(value_str.replace(",", ""))
                percent = int(percent_str)
                holdings_data.append({"Holding": name.strip(), "Value ($)": value, "% of Portfolio": percent})
            except:
                continue

        df_holdings = pd.DataFrame(holdings_data)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("💼 Portfolio Summary")
            st.metric("Net Portfolio Value", f"${portfolio_value}")

            if not df_holdings.empty:
                st.subheader("📋 Top Holdings")
                st.dataframe(df_holdings, use_container_width=True)
            else:
                st.warning("No holdings data found. Please check if your statement includes a holdings breakdown.")

        with col2:
            if not df_holdings.empty:
                st.subheader("🧩 Allocation")
                fig, ax = plt.subplots()
                ax.pie(df_holdings["% of Portfolio"], labels=df_holdings["Holding"], autopct='%1.1f%%', startangle=140)
                ax.axis('equal')
                st.pyplot(fig)

        if not df_holdings.empty:
            st.subheader("📈 Holdings Bar Chart")
            fig2, ax2 = plt.subplots()
            df_holdings_sorted = df_holdings.sort_values(by="Value ($)", ascending=False)
            ax2.barh(df_holdings_sorted["Holding"], df_holdings_sorted["Value ($)"])
            ax2.set_xlabel("Value ($)")
            ax2.set_title("Holdings Breakdown")
            st.pyplot(fig2)

        if openai_api_key and not df_holdings.empty:
            st.subheader("📝 AI-Powered Portfolio Summary")
            openai.api_key = openai_api_key
            try:
                prompt = """Summarize this investment portfolio in a professional, easy-to-understand tone for a client.\n\n""" + df_holdings.to_string(index=False)
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
                st.error(f"Failed to generate summary: {e}")

        st.markdown("---")
        st.info("This is a prototype dashboard. For best results, upload Fidelity monthly statements. Output may vary depending on formatting.")

except ModuleNotFoundError as e:
    print("\nERROR: Missing module. Please ensure all dependencies are installed.")
    print("\nError detail:", str(e))
    print("\nTo fix, run:")
    print("pip install streamlit pdfplumber matplotlib pandas openai")

except Exception as e:
    print("\nAn unexpected error occurred:", str(e))
