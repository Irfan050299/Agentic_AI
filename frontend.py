import streamlit as st
from backend import tools, llm, agent
from langchain_core.messages import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Agentic AI App 🤖", layout="wide")
st.title("Agentic AI Application 🤖")
st.markdown(
    "Interact with multiple AI agents. Ask anything related to:\n"
    "- DuckDuckGo search\n"
    "- Currency conversion (USD → INR)\n"
    "- Date & Time\n"
    "- Jokes"
)

# ------------------------------
# Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# ------------------------------

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
user_input = st.chat_input("You: ", key="input")

if user_input:
# For message show in Streamlit 
    st.session_state.messages.append({"role": "user", "content": user_input})
    
# Response to Agent
    response = agent.run(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")


