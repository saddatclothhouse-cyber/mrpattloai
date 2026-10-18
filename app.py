import streamlit as st
import google.generativeai as genai
import urllib.parse
import re
import random
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="ChatGPT", page_icon="✨", layout="wide")

# ChatGPT Deep Dark UI Styling
chatgpt_style = """
    <style>
    /* Streamlit default header footer hide */
    #MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Pure ChatGPT Background */
    .stApp {
        background-color: #212121;
        color: #ECECEC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Sidebar Styling like ChatGPT */
    section[data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2F2F2F;
    }
    
    /* Message Bubbles */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: 1px solid #2F2F2F;
        padding: 1.5rem 0.5rem;
    }
    
    /* Rounded Chat Input Box */
    div[data-testid="stChatInput"] {
        border-radius: 25px !important;
        border: 1px solid #424242 !important;
        background-color: #2F2F2F !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #707070 !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2F2F2F;
        color: #ECECEC;
        border: 1px solid #424242;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #424242;
        border-color: #606060;
    }
    </style>
"""
st.markdown(chatgpt_style, unsafe_allow_html=True)

# Hosted badges remover via script
components.html("""
<script>
setInterval(() => {
    try {
        window.top.document.querySelectorAll('[href*="streamlit.io"], div[class*="viewerBadge"], [data-testid="manage-app-button"]').forEach(el => {
            el.style.display = 'none';
        });
    } catch (e) {}
}, 250);
</script>
""", height=0)

# --- Chat History & Multi-Session Management ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"Chat 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Chat 1"

# --- Sidebar (ChatGPT Left Panel) ---
with st.sidebar:
    st.markdown("### ✨ **ChatGPT Pro**")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_name = f"Chat {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
        st.rerun()

    st.markdown("---")
    st.caption("🕒 **Recent Chats**")
    
    # List of past chats
    for session_name in list(st.session_state.sessions.keys()):
        if st.button(f"💬 {session_name}", key=session_name, use_container_width=True):
            st.session_state.current_session = session_name
            st.rerun()

# Current Active Chat
current_messages = st.session_state.sessions[st.session_state.current_session]

# Main Area Header
col_main, _ = st.columns([8, 1])
with col_main:
    st.markdown(f"#### **{st.session_state.current_session}**")

# Show Messages
for msg in current_messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"], caption=msg.get("caption", "Generated Image"))
        else:
            st.markdown(msg["content"])

# User Chat Input
prompt = st.chat_input("Message ChatGPT...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)

        # Hollywood / DALL-E 3 Level Prompt Engineering
        system_instruction = (
            "You are ChatGPT, an ultra-advanced AI. "
            "1. When the user asks to generate, create, draw, or make an image/thumbnail/artwork: "
            "You MUST act as a world-class prompt engineer (like DALL-E 3). "
            "Rewrite their concept into an ultra-detailed, photorealistic visual description. "
            "Include keywords: 'cinematic lighting, photorealistic, 8k resolution, volumetric light, award-winning composition, sharp focus, 3D typography'. "
            "If they asked for text (e.g. 'MR.PATLLO ENJOY FREE GIFT'), explicitly specify: 3D bold glossy gold text reading 'MR.PATLLO ENJOY FREE GIFT'. "
            "Format response ONLY as: [GENERATE_IMAGE: your detailed masterpiece prompt]. "
            "2. For general chat: Match the user's language (English, natural Roman Urdu, or Urdu script). "
            "Keep the tone smart, helpful, and natural like ChatGPT."
        )

        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=system_instruction
        )

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                resp_text = response.text.strip()

                if "[GENERATE_IMAGE:" in resp_text:
                    match = re.search(r'\[GENERATE_IMAGE:\s*(.*?)\]', resp_text)
                    raw_prompt = match.group(1).strip() if match else prompt
                    
                    # Aspect ratio check
                    is_wide = any(k in prompt.lower() for k in ["thumbnail", "youtube", "wide", "banner"])
                    w, h = (1280, 720) if is_wide else (1024, 1024)
                    
                    seed = random.randint(1, 9999999)
                    encoded = urllib.parse.quote(raw_prompt)
                    
                    # High-tier FLUX render without logos
                    image_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width={w}&height={h}&seed={seed}&nologo=true&enhance=true"
                    
                    st.image(image_url, caption="Generated with DALL-E Studio Mode")
                    current_messages.append({
                        "role": "assistant",
                        "type": "image",
                        "content": image_url,
                        "caption": "Generated with DALL-E Studio Mode"
                    })
                else:
                    st.markdown(resp_text)
                    current_messages.append({"role": "assistant", "content": resp_text})

    except Exception as e:
        st.error(f"Error: {e}")
