import streamlit as st
import boto3
import json
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage

# AWS Bedrock Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# LangChain memory for chat history
memory = ConversationBufferMemory(return_messages=True)

def get_bedrock_response(prompt):
    """Invoke Amazon Bedrock Claude 3.5 model to generate responses."""
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        response = bedrock_client.invoke_model(
            modelId=CLAUDE_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        response_body = json.loads(response["body"].read().decode("utf-8"))
        return response_body.get("content", ["Error: No response"])[0]
    except Exception as e:
        return f"Error calling Claude 3.5: {e}"

# Streamlit UI
st.title("AWS Bedrock Chatbot")
st.write("Chat with Claude 3.5 Sonnet using Amazon Bedrock!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    role, content = message
    if role == "user":
        st.text_area("You:", content, disabled=True)
    else:
        st.text_area("Claude 3.5:", content, disabled=True)

# User Input
user_input = st.text_input("Type your message here...")

if st.button("Send"):
    if user_input:
        # Append user input to LangChain memory
        memory.save_context({"input": user_input}, {"output": ""})

        # Get response from Claude 3.5
        response = get_bedrock_response(user_input)

        # Append Claude response to LangChain memory
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(response)

        # Update session state for chat history
        st.session_state.messages.append(("user", user_input))
        st.session_state.messages.append(("ai", response))

        # Display response
        st.text_area("Claude 3.5:", response, disabled=True)
    import streamlit as st
import boto3
import json
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage

# AWS Bedrock Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# LangChain memory for chat history
memory = ConversationBufferMemory(return_messages=True)

def get_bedrock_response(prompt):
    """Invoke Amazon Bedrock Claude 3.5 model to generate responses."""
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        response = bedrock_client.invoke_model(
            modelId=CLAUDE_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        # Parse response
        response_body = json.loads(response["body"].read().decode("utf-8"))
        
        # Ensure response is correctly formatted
        if isinstance(response_body, dict) and "content" in response_body:
            if isinstance(response_body["content"], list):
                return "\n".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in response_body["content"])
            elif isinstance(response_body["content"], str):
                return response_body["content"]
        
        return "Error: Unexpected response format from Claude"

    except Exception as e:
        return f"Error calling Claude 3.5: {e}"

# Streamlit UI
st.title("AWS Bedrock Chatbot")
st.write("Chat with Claude 3.5 Sonnet using Amazon Bedrock!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    role, content = message
    if role == "user":
        st.text_area("You:", content, disabled=True)
    else:
        st.text_area("Claude 3.5:", content, disabled=True)

# User Input
user_input = st.text_input("Type your message here...")

if st.button("Send"):
    if user_input:
        # Append user input to LangChain memory
        memory.save_context({"input": user_input}, {"output": ""})

        # Get response from Claude 3.5
        response = get_bedrock_response(user_input)

        # Append Claude response to LangChain memory
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(response)

        # Update session state for chat history
        st.session_state.messages.append(("user", user_input))
        st.session_state.messages.append(("ai", response))

        # Display response
        st.text_area("Claude 3.5:", response, disabled=True)
    
import streamlit as st
import boto3
import json
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage

# AWS Bedrock Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# LangChain memory for chat history
memory = ConversationBufferMemory(return_messages=True)

# Streamlit Page Config
st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for chat UI
st.markdown(
    """
    <style>
    .chat-container {
        max-width: 700px;
        margin: auto;
    }
    .chat-bubble-user {
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-end;
    }
    .chat-bubble-bot {
        background-color: #f1f0f0;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-start;
    }
    .message-box {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .message-box.user {
        align-items: flex-end;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def get_bedrock_response(prompt):
    """Invoke Amazon Bedrock Claude 3.5 model to generate responses."""
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        response = bedrock_client.invoke_model(
            modelId=CLAUDE_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        # Parse response
        response_body = json.loads(response["body"].read().decode("utf-8"))
        
        if isinstance(response_body, dict) and "content" in response_body:
            if isinstance(response_body["content"], list):
                return "\n".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in response_body["content"])
            elif isinstance(response_body["content"], str):
                return response_body["content"]
        
        return "Error: Unexpected response format from Claude"

    except Exception as e:
        return f"Error calling Claude 3.5: {e}"

# Sidebar
with st.sidebar:
    st.header("🤖 Chatbot Settings")
    st.write("Chat with Claude 3.5 Sonnet using Amazon Bedrock!")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []

# Chat UI
st.title("AWS Bedrock Chatbot 🤖")
st.markdown("### 💬 Chat with AI")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

chat_container = st.container()

# Display previous chat messages
with chat_container:
    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f'<div class="message-box user"><div class="chat-bubble-user">{content}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-box"><div class="chat-bubble-bot">{content}</div></div>', unsafe_allow_html=True)

# User Input
user_input = st.text_input("Type your message here...", key="input")

if st.button("Send"):
    if user_input:
        # Append user input to chat history
        st.session_state.messages.append(("user", user_input))

        # Show typing indicator
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input)

        # Append bot response to chat history
        st.session_state.messages.append(("bot", response))

        # Refresh page to update chat
        st.experimental_rerun()