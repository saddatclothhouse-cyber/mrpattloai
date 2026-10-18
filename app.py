import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Saddat Cloth AI Assistant", page_icon="🤖")

st.title("🤖 AI Assistant")
st.write("Khush-aamdeed! Main aapka AI assistant hoon. Main aapki kya madad kar sakta hoon?")

# Chupi hui API Key uthana
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani chat show karna
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Yahan apna sawal likhein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        model = genai.GenerativeModel("gemini-3.8-flash")
        with st.chat_message("assistant"):
            with st.spinner("Jawab tayyar ho raha hai..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error aya: {e}")
