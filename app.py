import streamlit as st
import google.generativeai as genai
import urllib.parse
import re

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="centered")

# Neeche aur ooper ke sab Streamlit badges/watermarks ko mukammal gayab karne ke liye CSS
hide_all_style = """
    <style>
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    [data-testid="stDecoration"] {visibility: hidden; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    div[class*="ProfileContainer"] {display: none !important;}
    div[class^="viewerBadge"] {display: none !important;}
    a[href*="streamlit.io"] {display: none !important;}
    </style>
"""
st.markdown(hide_all_style, unsafe_allow_html=True)

st.title("🤖 AI Assistant")
st.caption("Smart AI • Text Chat & High Quality Image Generation")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ChatGPT jese quick starter buttons
if len(st.session_state.messages) == 0:
    st.write("### How can I help you today?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎨 Create a realistic car"):
            st.session_state.starter_prompt = "Generate a photorealistic image of a luxury sports car parked on a modern city street"
    with col2:
        if st.button("💡 Ask anything"):
            st.session_state.starter_prompt = "Tell me 3 interesting facts about the universe."

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", "Generated Image"))
        else:
            st.markdown(message["content"])

# User prompt
prompt = st.chat_input("Message AI Assistant...")
if "starter_prompt" in st.session_state:
    prompt = st.session_state.pop("starter_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Prompt ko behtar samajhne aur exact image banane ki instruction
        system_instruction = (
            "You are an expert AI Assistant. "
            "1. When the user asks to create, draw, generate, or make an image/picture/photo, "
            "you MUST convert their exact request into a highly detailed, photorealistic visual English description. "
            "Format strictly as: [GENERATE_IMAGE: highly detailed English description with visual details]. "
            "Never ignore any detail the user mentioned. "
            "2. For regular questions: Respond politely matching the user's language. "
            "If user uses English -> reply in English. "
            "If user uses Roman Urdu -> reply in Roman Urdu. "
            "If user uses Urdu script -> reply in Urdu script."
        )
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=system_instruction
        )
        
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Image Generate karne ka block
                if "[GENERATE_IMAGE:" in response_text:
                    match = re.search(r'\[GENERATE_IMAGE:\s*(.*?)\]', response_text)
                    image_prompt = match.group(1).strip() if match else prompt
                    encoded = urllib.parse.quote(image_prompt)
                    
                    # FLUX AI model (Super realistic aur accurate image banata hai)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width=1024&height=1024&nologo=true&enhance=true"
                    
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
