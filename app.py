import streamlit as st
import google.generativeai as genai
import urllib.parse
import re
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="centered")

# CSS se header aur footer hide karna
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
    </style>
"""
st.markdown(hide_all_style, unsafe_allow_html=True)

# JavaScript se "Hosted with Streamlit" button ko bilkul khatam karna
components.html("""
<script>
function hideStreamlitBadges() {
    try {
        const topDoc = window.top.document;
        topDoc.querySelectorAll('[href*="streamlit.io"], div[class*="viewerBadge"], [data-testid="manage-app-button"]').forEach(el => {
            el.style.display = 'none';
            el.style.visibility = 'hidden';
        });
    } catch (e) {}
}
setInterval(hideStreamlitBadges, 300);
</script>
""", height=0)

st.title("🤖 AI Assistant")
st.caption("AI Assistant • High Definition Thumbnail & Image Generator")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", "Generated Image"))
        else:
            st.markdown(message["content"])

prompt = st.chat_input("Type your message or image request...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        system_instruction = (
            "You are a professional AI Assistant and expert Graphic/Thumbnail Designer. "
            "1. When the user asks for an image, thumbnail, banner, or drawing: "
            "If they mention text/words to write (e.g. 'MR.PATLLO ENJOY FREE GIFT'), YOU MUST include the text in quotes like: "
            "bold vibrant 3D text headline saying \"MR.PATLLO ENJOY FREE GIFT\". "
            "If they ask for a YouTube thumbnail, specify vibrant lighting, cinematic contrast, 16:9 ratio. "
            "Strictly output ONLY in this format: [GENERATE_IMAGE: detailed prompt]. "
            "2. For general talk: Match user language (English, Roman Urdu, or Urdu). Be polite and concise."
        )
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=system_instruction
        )
        
        with st.chat_message("assistant"):
            with st.spinner("Creating..."):
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                if "[GENERATE_IMAGE:" in response_text:
                    match = re.search(r'\[GENERATE_IMAGE:\s*(.*?)\]', response_text)
                    image_prompt = match.group(1).strip() if match else prompt
                    
                    # Thumbnail ratio ke liye 1280x720
                    is_thumbnail = any(k in prompt.lower() for k in ["thumbnail", "banner", "youtube", "wide"])
                    width, height = (1280, 720) if is_thumbnail else (1024, 1024)
                    
                    seed = random.randint(1, 999999)
                    encoded = urllib.parse.quote(image_prompt)
                    
                    # FLUX AI engine (text aur YouTube thumbnails ke liye best) bina kisi logo ke
                    image_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width={width}&height={height}&seed={seed}&nologo=true"
                    
                    st.image(image_url, caption="🎬 Generated Thumbnail")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "image",
                        "content": image_url,
                        "caption": "🎬 Generated Thumbnail"
                    })
                else:
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
    except Exception as e:
        st.error(f"Error: {e}")
