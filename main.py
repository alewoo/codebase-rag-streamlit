from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

st.title("ChatGPT-like clone")

# load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# initialize the OpenAI client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key,
)

if "groq_model" not in st.session_state:
    st.session_state["openai_model"] = "mixtral-8x7b-32768"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})