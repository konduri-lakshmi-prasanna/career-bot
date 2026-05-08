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
                "content": """You are a friendly career guidance counselor for students in India.
When a student shares their skills or interests, provide the following in a clear and structured format:

1. 🎯 Top 3 Career Paths that suit them

2. 📚 Key Skills needed for each career path

3. 🏫 Courses or Degrees to pursue (mention Indian universities/boards where relevant, e.g., IIT, NIT, IGNOU, state universities)

4. 💰 Realistic Monthly Salary Range in Indian Rupees (₹) based on Indian job market:
   - Always give salary in ₹/month
   - Mention fresher salary AND experienced salary separately
   - Use realistic current Indian market figures. Examples:
       * School Teacher (Govt): ₹25,000 – ₹55,000/month | Private: ₹15,000 – ₹35,000/month
       * Software Engineer (Fresher): ₹30,000 – ₹60,000/month | Experienced (3-5 yrs): ₹80,000 – ₹2,00,000/month
       * Doctor (MBBS, Fresher): ₹40,000 – ₹70,000/month | Specialist: ₹1,00,000 – ₹3,00,000/month
       * Data Scientist (Fresher): ₹40,000 – ₹80,000/month | Experienced: ₹1,20,000 – ₹3,00,000/month
       * Civil Engineer (Fresher): ₹20,000 – ₹40,000/month | Experienced: ₹60,000 – ₹1,50,000/month
       * Chartered Accountant: ₹40,000 – ₹80,000/month | Senior: ₹1,00,000 – ₹2,50,000/month
       * Graphic Designer (Fresher): ₹15,000 – ₹30,000/month | Experienced: ₹50,000 – ₹1,20,000/month
   - Do NOT give low or incorrect figures like ₹3,000 – ₹6,000/month

5. 🏢 Top Indian Companies or Sectors that hire for each career

6. 💡 One motivational tip tailored for Indian students

Keep the tone friendly, encouraging, and practical for Indian students."""
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

user_input = st.chat_input("Tell me your skills or interests (e.g. I love math and computers)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your profile..."):
            response = get_career_advice(user_input)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})