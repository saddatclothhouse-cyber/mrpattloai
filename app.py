import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Assistant", page_icon="🤖")

# Top header aur extra menu chupane ke liye
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Dashboard pure English mein
st.title("🤖 AI Assistant")
st.write("Welcome! How can I assist you today?")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # AI ko zuban samajhne ki instruction di hai
        system_instruction = (
            "You are a professional AI Assistant. "
            "Always match the language of the user: "
            "1. If the user writes in English, reply strictly in English. "
            "2. If the user writes in Roman Urdu (Urdu written in English alphabets like 'kya haal hai'), reply naturally in polite Roman Urdu. "
            "3. If the user writes in Urdu script, reply in Urdu. "
            "Be concise, polite, and helpful."
        )
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=system_instruction
        )
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error: {e}")
