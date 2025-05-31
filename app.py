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

        holdings_match = re.search(r"Top Holdings\n(.*?)Asset Allocation", text, re.DOTALL)
        holdings_text = holdings_match.group(1).strip() if holdings_match else ""
        holdings_lines = [
            line.strip() for line in holdings_text.split('\n')
            if line.strip() and not line.startswith("Description") and not line.startswith("Total")
        ]

        holdings_data = []
        for line in holdings_lines:
            match = re.match(r"(.+?)\s+\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(\d+)%", line)
            if match:
                name = match.group(1).strip()
                value = float(match.group(2).replace(",", ""))
                percent = int(match.group(3))
                holdings_data.append({"Holding": name, "Value ($)": value, "% of Portfolio": percent})

        df_holdings = pd.DataFrame(holdings_data)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("💼 Portfolio Summary")
            st.metric("Net Portfolio Value", f"${portfolio_value}")

            if not df_holdings.empty:
                st.subheader("📋 Top Holdings")
                st.dataframe(df_holdings, use_container_width=True)

        with col2:
            if not df_holdings.empty:
                st.subheader("🧩 Allocation")
                fig, ax = plt.subplots()
                ax.pie(df_holdings["% of Portfolio"], labels=df_holdings["Holding"], autopct='%1.1f%%', startangle=140)
                ax.axis('equal')
                st.pyplot(fig)

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
