import streamlit as st
import google.generativeai as genai
import os
import time
from streamlit_chat import message

# Load API Key from Streamlit secrets
api_key = st.secrets["general"]["google_api_key"]

if not api_key:
    st.error("API Key not found. Please check your .streamlit/secrets.toml file.")
    st.stop()

genai.configure(api_key=api_key)

# Streamlit UI Configuration
st.set_page_config(page_title="🩺 AI Medical Chatbot", page_icon="🩺", layout="wide")

# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
menu_selection = st.sidebar.radio("Go to", ["🏠 Home", "💬 Chatbot", "📜 History"])

# New Chat Button
st.sidebar.markdown("---")
if st.sidebar.button("➕ New Chat"):
    st.session_state.current_chat_id = None  # Reset active chat
    st.rerun()

# Initialize Chat History
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}  # Stores multiple chats
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None  # Tracks the active chat

# Function to generate a unique chat ID
def generate_chat_id():
    return str(int(time.time()))  # Timestamp-based unique ID

# ✅ Home Section
if menu_selection == "🏠 Home":
    st.title("🏠 Welcome to AI Medical Chatbot")
    st.write(""" 
    **This AI-powered chatbot provides instant health-related information.**  
    You can ask about:
    - First aid tips  
    - Symptoms of common illnesses  
    - Preventive healthcare advice  
    - And much more!  

    ⚠️ **Disclaimer:** This chatbot is for general information only and **not** a substitute for professional medical advice.  
    Always consult a healthcare provider for serious concerns.
    """)

# ✅ Chatbot Section
elif menu_selection == "💬 Chatbot":
    st.title("🩺 AI Medical Chatbot")
    st.write("Ask me anything about health, medicine, or biology.")

    # Start a new chat if none is active
    if not st.session_state.current_chat_id:
        new_chat_id = generate_chat_id()
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chat_histories[new_chat_id] = {
            "title": "Unnamed Chat",
            "messages": [
                {"role": "assistant", "content": "Hello! How can I assist you with medical or health-related questions today?"}
            ]
        }

    # Load the active chat
    chat_id = st.session_state.current_chat_id
    chat_data = st.session_state.chat_histories[chat_id]
    chat_messages = chat_data["messages"]

    # Display chat history
    for msg in chat_messages:
        if isinstance(msg, dict) and "role" in msg:
            message(msg["content"], is_user=(msg["role"] == "user"))

    # User input
    user_text = st.chat_input("Type your message here...")  # Auto clears after submission

    if user_text:
        chat_messages.append({"role": "user", "content": user_text.strip()})
        message(user_text, is_user=True)  # Show user message instantly

        # Auto-name chat based on first user message
        if chat_data["title"] == "Unnamed Chat" and len(chat_messages) == 2:
            chat_data["title"] = user_text[:30] + "..." if len(user_text) > 30 else user_text
            st.session_state.chat_histories[chat_id] = chat_data

        # AI is typing...
        with st.spinner("AI is thinking..."):
            try:
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(user_text.strip())
                ai_response = response.text if hasattr(response, "text") else "I'm sorry, an issue occurred."
            except Exception:
                ai_response = "I'm sorry, an error occurred. Please try again."

        # Store AI response
        chat_messages.append({"role": "assistant", "content": ai_response})
        message(ai_response, is_user=False)

# ✅ History Section
elif menu_selection == "📜 History":
    st.title("📜 Chat History")

    if not st.session_state.chat_histories:
        st.info("No chat history found.")
    else:
        for chat_id, chat in list(st.session_state.chat_histories.items()):
            chat_title = chat.get("title", "Unnamed Chat")

            col1, col2 = st.columns([0.85, 0.15])

            with col1:
                if st.button(f"📂 {chat_title}", key=f"chat_{chat_id}"):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()

            with col2:
                with st.expander("⋮"):  # Three-dot menu
                    new_title = st.text_input("Rename Chat", value=chat_title, key=f"rename_{chat_id}")
                    col_btn1, col_btn2 = st.columns([0.5, 0.5])
                    with col_btn1:
                        if st.button("✅ Save", key=f"save_{chat_id}"):
                            if new_title.strip():
                                st.session_state.chat_histories[chat_id]["title"] = new_title.strip()
                                st.rerun()
                    with col_btn2:
                        if st.button("🗑️ Delete", key=f"delete_{chat_id}"):
                            del st.session_state.chat_histories[chat_id]
                            st.rerun()

    if st.button("🗑️ Clear All History"):
        st.session_state.chat_histories = {}
        st.session_state.current_chat_id = None
        st.success("Chat history cleared successfully!")
        st.rerun()
