import streamlit as st
from datetime import datetime
from stockInfo import stockAnalyzer
st.set_page_config(
    page_title="Financial Insights",
    page_icon="💰",  
)
st.title("🔗Financial Insights LLM🚀")
st.write("Gain Financial Insights on a publicly traded company📈")

query = st.text_input('Input the Company name 🤑')

Enter = st.button("Analyze 💎")

if Enter:
    if not query:
        st.warning("Please enter a company name.")
    else:
        try:
            with st.spinner('Processing... ⌛'):
                result = stockAnalyzer(query)
            st.success('Analysis done!💰')
            st.write(result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def downloadAnalysis(analysis_text, filename):
    with open(filename, 'w') as file:
        file.write(analysis_text)

if st.button("Download Analysis"):
    if not result:
        st.warning("Please enter a company first.")
    else:
        filename = f"stock_analysis_{query}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        downloadAnalysis(result, filename)
        st.success(f"Analysis downloaded successfully as {filename}!")
