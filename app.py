import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Career Guidance Bot", page_icon="🎯", layout="centered")
st.title("🎯 Career Guidance Chatbot")
st.markdown("**Tell me your skills or interests — I'll suggest career paths!**")
st.divider()

def get_career_advice(user_input):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a friendly career guidance counselor for students.
When a student shares their skills or interests, provide:
1. 🎯 Top 3 career paths that suit them
2. 📚 Key skills needed for each path
3. 🏫 Courses or degrees to pursue
4. 💰 Approximate entry-level salary range
5. 💡 One motivational tip
Keep it clear, structured, and encouraging."""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )
    return response.choices[0].message.content

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Tell me your skills or interests...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your profile..."):
            response = get_career_advice(user_input)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})