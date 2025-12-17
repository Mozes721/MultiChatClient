import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.abstract_methods import BotMethods
from model.llm import LLM

class LocalBot(BotMethods):
    def __init__(self) -> None:
        self.initialize_session_state()
        self.llm = LLM()  # LLM handles classification, RAG, and response generation
        st.title("Stock, Crypto, and Weather Bot")

    def initialize_session_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def get_response(self, user_message: str) -> str:
        """Generate response - LLM handles everything."""
        return self.llm.generate(user_message)

    def display_chat_history(self):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def get_user_input(self):
        return st.chat_input("What is up?")

    def run(self):
        self.display_chat_history()

        if prompt := self.get_user_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response from LLM
            response = self.get_response(prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    bot = LocalBot()
    bot.run()