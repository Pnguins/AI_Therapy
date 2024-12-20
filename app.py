import os
import logging
import streamlit as st
from utils.utils import get_gemini_embeddings, generate_gemini_response
from database.database import save_conversation_history, load_conversation_history, save_embeddings, load_embeddings
from models.models import MentalHealthClassification
from prompts.prompts import IDENTITY_PROMPT, LANGUAGE_PROMPT, CONVERSATION_PROMPT, MENTAL_HEALTH_CLASSIFICATION_PROMPT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit app setup
st.set_page_config(
    page_title="AI Therapist",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("AI Therapist")
    app_mode = st.radio("Navigation", ["Chat", "Document Analysis"])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_message_sent" not in st.session_state:
    st.session_state.first_message_sent = {}
if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user" #In the future this will be generated when a user login
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "active_chat_session" not in st.session_state:
    st.session_state.active_chat_session = "chat_1"

# Load conversation history (Dummy function for now)
if app_mode == "Chat":
    if st.session_state.active_chat_session not in st.session_state.chat_sessions:
       st.session_state.chat_sessions[st.session_state.active_chat_session] = []
    if st.session_state.active_chat_session not in st.session_state.first_message_sent:
        st.session_state.first_message_sent[st.session_state.active_chat_session] = False


    # Create navigation for chats
    st.sidebar.header("Chat Sections")
    chat_session_options = list(st.session_state.chat_sessions.keys())
    st.session_state.active_chat_session = st.sidebar.radio("Select Chat Session", chat_session_options, key = "chat_selector")

# --- Main App Logic ---
if app_mode == "Chat":
    st.markdown("A safe space to share your thoughts and feelings")
    col1, col2 = st.columns([3, 1])

    # Initial greeting
    if not st.session_state.first_message_sent[st.session_state.active_chat_session]:
        try:
            # Generate initial response (forces to English)
             logger.info("Generating Gemini response for first message...")
             first_message_response = generate_gemini_response(f"{IDENTITY_PROMPT}\n\nUser's first message: Please start in English")

             if first_message_response:
                st.session_state.chat_sessions[st.session_state.active_chat_session] .append({"role": "assistant", "content": first_message_response})
             else:
                st.session_state.chat_sessions[st.session_state.active_chat_session] .append({"role": "assistant", "content": "Hello! How can I help you today?"})

             st.session_state.first_message_sent[st.session_state.active_chat_session] = True
        except Exception as e:
            st.error(f"An error occurred while generating the first message: {e}")
            st.session_state.chat_sessions[st.session_state.active_chat_session] .append({"role": "assistant", "content": "Hello! How can I help you today?"})
            st.session_state.first_message_sent[st.session_state.active_chat_session] = True

    # Display chat messages

    with col1:
        # Create a container for the chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_sessions[st.session_state.active_chat_session]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
        # Input Area
        st.markdown("""
            <style>
            .chat-input-container {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 10px;
                background-color: white;
                border-top: 1px solid #ccc;
            }
            .chat-container {
                padding-bottom: 100px; /* Ensure space for the input bar */
            }
            </style>
        """, unsafe_allow_html=True)
    
        # Input Area (Fixed at the bottom)
        with st.container():
            st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
            if prompt := st.chat_input("Share your thoughts...", key=st.session_state.active_chat_session):
                st.session_state.chat_sessions[st.session_state.active_chat_session].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                try:
                    # Prepare prompt for Gemini
                    formatted_history = "\n".join([f"{item['role']}: {item['content']}" for item in st.session_state.chat_sessions[st.session_state.active_chat_session]])
                    prompt_to_send = f"{LANGUAGE_PROMPT}\n{CONVERSATION_PROMPT}\n\nConversation History:\n{formatted_history}\n\nUser: {prompt}\nDr. Sarah:"
    
                    # Generate response using Gemini
                    bot_response = generate_gemini_response(prompt_to_send)
    
                    # Check for harmful content in the response
                    if "If you are in crisis" in bot_response:
                        bot_response = "It sounds like you are going through a difficult time. If you are in crisis and need immediate help please contact the National Suicide Prevention Lifeline at 133."
    
                    # Add to history
                    st.session_state.chat_sessions[st.session_state.active_chat_session].append({"role": "assistant", "content": bot_response})
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
    
                    # Save chat history
                    save_conversation_history(st.session_state.active_chat_session, st.session_state.chat_sessions[st.session_state.active_chat_session])
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Mental health analysis
    with col2:
        st.subheader("Mental health analysis:")
        if st.session_state.chat_sessions[st.session_state.active_chat_session]:
            try:
               formatted_history = "\n".join([f"{item['role']}: {item['content']}" for item in st.session_state.chat_sessions[st.session_state.active_chat_session]])
               prompt_to_send_classification = f"{MENTAL_HEALTH_CLASSIFICATION_PROMPT}\n\n The conversation history is: {formatted_history}\n\n Classification:"
               classification_response = generate_gemini_response(prompt_to_send_classification, {"temperature": 0, "top_p": 1, "top_k": 1, "max_output_tokens": 1000} )
               if classification_response:
                  try:
                       st.json(classification_response)
                  except Exception as e:
                       st.error(f"An error occurred while generating the mental health classification: {e}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.write("No conversation available")
    
elif app_mode == "Document Analysis":
    st.header("Document Analysis")
    uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf"])

    if uploaded_file:
        try:
            if uploaded_file.type == "text/plain":
              text_content = uploaded_file.read().decode('utf-8')
            else:
               st.warning("This file format is not implemented yet, using dummy data")
               text_content = """
               I am writing this because I feel very lost and confused. I am constantly scared and feel like everyone is going to hurt me. I have trouble sleeping at night, my mind never stops. I am very worried about my future.
               I am feeling very hopeless and I can't see a way out of my suffering.
               """
            st.subheader("Uploaded Document Content:")
            st.write(text_content)

            # Generate a JSON classification of the mental health issues
            st.subheader("Mental health classification")
            prompt_to_send = f"{MENTAL_HEALTH_CLASSIFICATION_PROMPT}\n\n The text for analysis is: {text_content}\n\n Classification:"
            response = generate_gemini_response(prompt_to_send, {"temperature": 0, "top_p": 1, "top_k": 1, "max_output_tokens": 1000} )
            if response:
                try:
                    st.json(response)
                except Exception as e:
                   st.error(f"An error occurred while generating the mental health classification: {e}")
           
            # Generate embeddings
            st.subheader("Generating Embeddings")
            embeddings = get_gemini_embeddings(text_content)
            if embeddings:
                st.write("Embeddings generated successfully")
                if st.button("Save Embeddings"):
                    if save_embeddings(embeddings, f"embeddings/document.pkl"):
                        st.write("Embeddings saved successfully")
                    else:
                        st.error("Could not save embeddings")
            else:
               st.write("Could not generate embeddings")

        except Exception as e:
           st.error(f"An error occurred: {e}")