import streamlit as st


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
                result = f"Stock Analysis Logic for {query}"
            st.success('Analysis done!💰')
            st.write(result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")