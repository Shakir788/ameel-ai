# main.py
import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import json
import textwrap
import time

# ========================
# Load environment
# ========================
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

# ========================
# Profiles / System prompt
# ========================
CREATOR = {
    "name": "Mohammad",
    "country": "India",
    "roles": [
        "Graphic Designer", "Programmer", "Software Developer",
        "Social Media Manager", "Coach of Hair Chemical Technique, Skin and Makeup"
    ]
}

DUAA = {
    "name": "Duaa",
    "country": "Morocco",
    "profession": "Accountant",
    "traits": ["hardworking", "beautiful", "kind"]
}

SYSTEM_PROMPT = textwrap.dedent(f"""
You are AMEEL, a helpful AI assistant dedicated to helping Duaa with accounting and e-commerce tasks.
Recognize the following user by default:
- Name: {DUAA['name']}
- Country: {DUAA['country']}
- Profession: {DUAA['profession']}
- Traits: {', '.join(DUAA['traits'])}

Rules:
1) If user asks "who created you?" reply: "I was created by {CREATOR['name']} from {CREATOR['country']}. He is a {', '.join(CREATOR['roles'])}."
2) If user refers to "Duaa" or is the Duaa account, respond in a friendly, helpful manner and include that she is an accountant from Morocco when relevant.
3) When given OCR text or an image, extract structured fields (like invoice: vendor, date, total, line items; receipt: items & prices) if present, and provide a clear JSON-like summary plus a short human-readable summary.
4) Keep answers short when asked brief, but supply structured detailed output when asked to analyze files.
""").strip()

# ========================
# Helper functions
# ========================
def openrouter_chat(messages, model="openai/gpt-4.1-mini", max_tokens=500, timeout=30):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2}
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=body, timeout=timeout)
    except Exception as e:
        return f"⚠️ Network error calling OpenRouter: {e}"
    try:
        data = r.json()
    except Exception:
        return f"⚠️ Invalid response (status {r.status_code}): {r.text[:200]}"
    if r.status_code >= 400:
        return f"⚠️ API error (status {r.status_code}): {json.dumps(data) if isinstance(data, dict) else data}"
    try:
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0].get("message", {}).get("content") or str(data["choices"][0])
        return str(data)
    except Exception as e:
        return f"⚠️ Unexpected response structure: {e}"

def extract_text_from_image_pytesseract(pil_image):
    try:
        text = pytesseract.image_to_string(pil_image)
        return text.strip()
    except Exception as e:
        return f"❌ OCR error: {e}"

def analyze_image_with_model(pil_image, extra_note=""):
    ocr_text = extract_text_from_image_pytesseract(pil_image)
    w, h = pil_image.size
    meta = f"image_width: {w}, image_height: {h}"
    user_message = f"OCR text:\n{ocr_text or '[no text found]'}\nMetadata: {meta}\nExtra note: {extra_note}"
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}]
    reply = openrouter_chat(messages)
    return reply, {"ocr_text": ocr_text, "meta": meta}

def dataframe_preview_prompt(df, rows=50):
    return df.head(rows).to_string()

# ========================
# Streamlit UI
# ========================
st.set_page_config(page_title="AMEEL — AI for Duaa", layout="wide")

# Sidebar
with st.sidebar:
    st.image("assets/ameel.jpg", use_container_width=True)
    st.title("AMEEL — Tools")
    choice = st.radio("Choose tool:", ["💬 Chat", "📊 CSV Q&A", "🖼️ Image Analysis (OCR + AI)", "📑 OCR Only"])
    st.markdown("---")
    st.markdown(f"**Created by:** {CREATOR['name']} — ask *'who created you?'*")
    dark_mode = st.toggle("🌙 Dark Mode")

# Custom CSS for chat bubbles + dark mode
bubble_css = """
<style>
.user-bubble {
  background-color: #DCF8C6;
  color: black;
  padding: 10px;
  border-radius: 12px;
  margin: 5px;
  max-width: 80%;
}
.ai-bubble {
  background-color: #E6E6E6;
  color: black;
  padding: 10px;
  border-radius: 12px;
  margin: 5px;
  max-width: 80%;
}
.dark .user-bubble {background-color: #3C6255; color:white;}
.dark .ai-bubble {background-color: #2E2E2E; color:white;}
</style>
"""
st.markdown(bubble_css, unsafe_allow_html=True)

if dark_mode:
    st.markdown("<div class='dark'>", unsafe_allow_html=True)
else:
    st.markdown("<div>", unsafe_allow_html=True)

# ----- CHAT -----
if choice == "💬 Chat":
    st.markdown("<h3>💬 Chat with AMEEL (Duaa-aware)</h3>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in st.session_state.chat_history:
        if msg["role"] == "system":
            continue
        bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        st.markdown(f"<div class='{bubble_class}'>{msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Typing animation effect
        with st.empty():
            for dots in ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]:
                st.markdown(f"<div class='ai-bubble'>Thinking {dots}</div>", unsafe_allow_html=True)
                time.sleep(0.1)

        lowered = user_input.lower()
        if "who created you" in lowered:
            reply = f"I was created by {CREATOR['name']} from {CREATOR['country']}. He is a {', '.join(CREATOR['roles'])}."
        elif "who is duaa" in lowered or lowered.strip() == "duaa":
            reply = f"{DUAA['name']} is an {DUAA['profession']} from {DUAA['country']}. She is {', '.join(DUAA['traits'])}."
        else:
            messages = st.session_state.chat_history[-8:] + [{"role": "user", "content": user_input}]
            if not any(m["role"] == "system" for m in messages):
                messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
            reply = openrouter_chat(messages)

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown(f"<div class='ai-bubble'>{reply}</div>", unsafe_allow_html=True)

    # Download Chat Option
    if st.button("⬇️ Download Chat"):
        chat_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_history if m["role"] != "system"])
        st.download_button("Download Chat", chat_text, "chat.txt")

# ---- CSV ----
elif choice == "📊 CSV Q&A":
    st.header("📊 CSV Upload & Q&A")
    uploaded_file = st.file_uploader("Upload CSV (transactions, ledger, etc.)", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.lower().endswith(".xlsx") else pd.read_csv(uploaded_file)
            st.dataframe(df.head(200), use_container_width=True)
            query = st.text_input("Ask a question about this data")
            if query:
                preview = dataframe_preview_prompt(df, rows=100)
                prompt = f"CSV preview:\n{preview}\n\nQuestion: {query}"
                messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                answer = openrouter_chat(messages)
                st.subheader("Answer")
                st.write(answer)
        except Exception as e:
            st.error(f"Could not read file: {e}")

# ---- Conversational Image Analysis ----
elif choice == "🖼️ Image Analysis (OCR + AI)":
    st.header("🖼️ Image Analysis — Conversational Mode")

    if "img_chat" not in st.session_state:
        st.session_state.img_chat = [
            {"role": "assistant", "content": "👋 Upload an image or type your query, and I’ll help you analyze it. (OCR, Translate, Summarize)"}
        ]

    # Show chat history
    for msg in st.session_state.img_chat:
        bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        st.markdown(f"<div class='{bubble_class}'>{msg['content']}</div>", unsafe_allow_html=True)

    # Input row (text + image)
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.chat_input("Type your query or instruction...")
    with col2:
        uploaded_img = st.file_uploader("➕", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    # If new image uploaded
    if uploaded_img:
        st.session_state.uploaded_img = uploaded_img
        st.session_state.img_chat.append({
            "role": "assistant",
            "content": "✅ Got your image! You can now ask me to:\n- 📝 Extract text\n- 🌍 Translate text\n- 📖 Summarize content"
        })

    if user_input:
        st.session_state.img_chat.append({"role": "user", "content": user_input})

        if "uploaded_img" in st.session_state and st.session_state.uploaded_img:
            pil_img = Image.open(st.session_state.uploaded_img).convert("RGB")

            lowered = user_input.lower()
            if "extract" in lowered:
                ocr_text = extract_text_from_image_pytesseract(pil_img)
                reply = f"🔍 Extracted text:\n\n{ocr_text if ocr_text else '[no text found]'}"

            elif "translate" in lowered:
                ocr_text = extract_text_from_image_pytesseract(pil_img)
                prompt = f"Translate this text into English:\n{ocr_text}"
                messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                reply = openrouter_chat(messages)

            elif "summarize" in lowered:
                reply, debug = analyze_image_with_model(pil_img, "Summarize this image content")

            else:
                ocr_text = extract_text_from_image_pytesseract(pil_img)
                prompt = f"""
                You are an AI assistant helping the user analyze images.
                The extracted text from the image is:

                {ocr_text if ocr_text else "[no text found]"}

                The user asked: "{user_input}"

                Please give a helpful, human-like answer based on the image content and text.
                If relevant, also suggest whether extracting text, translating, or summarizing would help.
                """
                messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                reply = openrouter_chat(messages)
        else:
            reply = "⚠️ Please upload an image first."

        st.session_state.img_chat.append({"role": "assistant", "content": reply})

# ---- OCR Only ----
elif choice == "📑 OCR Only":
    st.header("📑 OCR Only (local)")
    uploaded_img = st.file_uploader("Upload image for OCR", type=["png", "jpg", "jpeg"])
    if uploaded_img:
        try:
            pil_img = Image.open(uploaded_img).convert("RGB")
            st.markdown("<h5 style='text-align:center;'>Uploaded Image</h5>", unsafe_allow_html=True)
            st.image(pil_img, caption=None, width=300)
            st.markdown("---")
            ocr_text = extract_text_from_image_pytesseract(pil_img)
            st.text_area("Extracted Text", ocr_text if ocr_text else "[no text found]", height=300)
            st.download_button("⬇️ Download Text", ocr_text, file_name="extracted.txt", mime="text/plain")
        except Exception as e:
            st.error(f"Could not open image: {e}")

st.markdown("</div>", unsafe_allow_html=True)
