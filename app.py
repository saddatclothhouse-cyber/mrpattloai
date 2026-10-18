import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="My AI Chatbot", page_icon="🤖")

st.title("🤖 Smart AI Assistant")
st.write("Mera live AI chatbot! Neeche koi bhi sawal poochein:")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Yahan likhein..."):
    if not api_key:
        st.warning("Pehle left menu (sidebar) mein apni Gemini API Key daalein!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            with st.chat_message("assistant"):
                with st.spinner("AI soch raha hai..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
