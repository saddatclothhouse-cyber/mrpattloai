import streamlit as st
import google.generativeai as genai
import urllib.parse
import re

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="centered")

# ChatGPT jaisa clean look aur sab buttons chupana
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden; display: none;}
    header {visibility: hidden; display: none;}
    footer {visibility: hidden; display: none;}
    [data-testid="stToolbar"] {visibility: hidden; display: none;}
    [data-testid="stDecoration"] {visibility: hidden; display: none;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title("🤖 AI Assistant")
st.caption("Powered by Gemini AI • Supports Chat & Free Image Generation")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ChatGPT jese Quick Starter Buttons (jab chat khali ho)
if len(st.session_state.messages) == 0:
    st.write("### How can I help you today?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎨 Create an image of a cyber car"):
            st.session_state.starter_prompt = "Create an image of a futuristic neon cyber sports car"
    with col2:
        if st.button("💡 Explain how AI works"):
            st.session_state.starter_prompt = "Explain how Artificial Intelligence works in simple words."

# Chat history display karna
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", "Generated Image"))
        else:
            st.markdown(message["content"])

# User prompt lena (input box se ya starter button se)
prompt = st.chat_input("Message AI Assistant...")
if "starter_prompt" in st.session_state:
    prompt = st.session_state.pop("starter_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        system_instruction = (
            "You are a professional ChatGPT-like AI Assistant. "
            "1. If the user asks to generate, create, draw, or make an image/picture/photo, "
            "strictly respond with ONLY this format: [GENERATE_IMAGE: descriptive English visual prompt]. "
            "2. For normal text questions: Always match the language of the user. "
            "If they write in English, reply in English. "
            "If they write in Roman Urdu (Urdu in English alphabet like 'kya haal hai'), reply naturally in polite Roman Urdu. "
            "If they write in Urdu script, reply in Urdu. Be concise, clear, and helpful."
        )
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=system_instruction
        )
        
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Check karein agar user ne image mangi hai
                if "[GENERATE_IMAGE:" in response_text:
                    match = re.search(r'\[GENERATE_IMAGE:\s*(.*?)\]', response_text)
                    image_prompt = match.group(1).strip() if match else prompt
                    encoded = urllib.parse.quote(image_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                    
                    st.image(image_url, caption=f"🎨 {image_prompt}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "image",
                        "content": image_url,
                        "caption": f"🎨 {image_prompt}"
                    })
                else:
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
    except Exception as e:
        st.error(f"Error: {e}")
