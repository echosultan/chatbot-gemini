import os
import streamlit as st
from google import genai

# Konfigurasi halaman
st.set_page_config(
    page_title="Gemini AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Inisialisasi aplikasi
st.title("🤖 Gemini AI Chatbot")
st.caption("Chatbot AI berbasis Google Gemini")

# Ambil API key dari Streamlit Secrets atau environment variable
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "API key Gemini belum dikonfigurasi. "
        "Tambahkan GEMINI_API_KEY di pengaturan Secrets."
    )
    st.stop()

# Inisialisasi Gemini
client = genai.Client(api_key=api_key)

# Pilihan model
MODEL = "gemini-2.5-flash"

# Instruksi chatbot
SYSTEM_PROMPT = """
Kamu adalah asisten AI yang ramah, informatif, dan membantu.
Jawab pertanyaan pengguna dalam bahasa yang mereka gunakan.
Berikan jawaban yang jelas dan mudah dipahami.
Jika tidak mengetahui jawabannya, katakan dengan jujur.
"""

# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tombol hapus percakapan
if st.sidebar.button("🗑️ Hapus percakapan"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("### Tentang chatbot")
st.sidebar.write(
    "Chatbot ini menggunakan Google Gemini "
    "dan Streamlit untuk menghasilkan jawaban AI."
)

# Tampilkan riwayat percakapan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input pesan pengguna
prompt = st.chat_input("Tulis pertanyaanmu di sini...")

if prompt:
    # Tampilkan pesan pengguna
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Buat jawaban menggunakan Gemini
    with st.chat_message("assistant"):
        try:
            with st.spinner("Gemini sedang berpikir..."):
                history = []

                for message in st.session_state.messages[:-1]:
                    history.append({
                        "role": "user" if message["role"] == "user"
                        else "model",
                        "parts": [{"text": message["content"]}]
                    })

                chat = client.chats.create(
                    model=MODEL,
                    history=history,
                    config={
                        "system_instruction": SYSTEM_PROMPT,
                        "temperature": 0.7,
                    },
                )

                response = chat.send_message(prompt)
                answer = response.text or "Gemini tidak memberikan jawaban."

            st.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error(
                "Maaf, terjadi kesalahan saat menghubungi Gemini. "
                "Periksa API key, koneksi internet, dan ketersediaan model."
            )
            st.caption(f"Detail error: {e}")