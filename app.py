import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from prompts import SYSTEM_PROMPT, PRESSURE_TEST_PROMPT

# Load secret API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Configure Groq client
client = Groq(api_key=api_key)

# Page config
st.set_page_config(
    page_title="PRD Agent",
    page_icon="??",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("?? PRD Agent")
st.subheader("From blank page to first draft in minutes")

st.markdown("""
**How it works:**
1. Answer 5 quick questions about your product
2. Get a structured PRD draft
3. Enter pressure-test mode to challenge your assumptions
4. Export when ready
""")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hi! I'm your PRD drafting assistant. Let's build your PRD. \n\n**Question 1 of 5:** What's your product called, and what does it do in one sentence?"}
    ]
    st.session_state.prd_generated = False

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Type your answer here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                temperature=0.7
            )
            ai_message = response.choices[0].message.content
            
            st.markdown(ai_message)
            st.session_state.messages.append({"role": "assistant", "content": ai_message})
            
            if "## 1." in ai_message and not st.session_state.prd_generated:
                st.session_state.prd_generated = True
                st.balloons()
                st.success("?? PRD Draft Generated! Scroll up to review or continue chatting to refine.")

# Sidebar with controls
with st.sidebar:
    st.header("Controls")
    
    if st.button("?? Enter Pressure-Test Mode"):
        st.session_state.messages.append({
            "role": "user", 
            "content": "Please enter pressure-test mode and challenge this PRD."
        })
        st.session_state.messages.append({
            "role": "system", 
            "content": PRESSURE_TEST_PROMPT
        })
        st.rerun()
    
    st.divider()
    
    if st.button("??? Start New PRD"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Hi! I'm your PRD drafting assistant. Let's build your PRD. \n\n**Question 1 of 5:** What's your product called, and what does it do in one sentence?"}
        ]
        st.session_state.question_count = 1
        st.session_state.prd_generated = False
        st.rerun()
    
    st.divider()
    
    st.subheader("Export PRD")
    
    prd_content = ""
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and "## 1." in msg["content"]:
            prd_content = msg["content"]
            break
    
    if prd_content:
        st.download_button(
            label="?? Download as Markdown",
            data=prd_content,
            file_name="prd-draft.md",
            mime="text/markdown"
        )
    else:
        st.info("Complete the questions to enable export.")

st.divider()
st.caption("Built for PMs, by a PM. Questions? Check the GitHub repo.")
