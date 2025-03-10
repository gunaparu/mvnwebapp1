import streamlit as st
import boto3
import json
import uuid
from langchain.memory import ConversationBufferMemory

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "your-security-bucket"  # Update with your S3 bucket name
SECURITY_GUIDELINES_FILE = "security_guidelines.txt"  # Stored in S3

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Streamlit Page Config
st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")

# Handle Unique Chat Sessions via URL Parameters
query_params = st.query_params
chat_id = query_params.get("chat_id", str(uuid.uuid4()))  # Generate if not present
st.query_params["chat_id"] = chat_id  # Ensure URL has chat_id

# Initialize Memory for the Chat Session
if f"memory_{chat_id}" not in st.session_state:
    st.session_state[f"memory_{chat_id}"] = ConversationBufferMemory()
if f"messages_{chat_id}" not in st.session_state:
    st.session_state[f"messages_{chat_id}"] = []

# Function to Fetch Security Guidelines
def get_security_guidelines():
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

# Function to Call AWS Bedrock (Claude 3.5)
def get_bedrock_response(prompt, chat_history, security_guidelines):
    full_prompt = f"""
    Previous Conversation: {chat_history}
    
    User Query: {prompt}
    
    Security Guidelines Reference:
    {security_guidelines}

    Claude:
    """
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": full_prompt}],
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

# Sidebar Controls
with st.sidebar:
    st.header("🤖 Chatbot Settings")

    # Generate a new unique chat ID
    new_chat_id = str(uuid.uuid4())
    new_chat_url = f"{st.get_option('server.baseUrlPath')}?chat_id={new_chat_id}"

    # Button to open a new chat window
    st.link_button("➕ New Chat", new_chat_url, use_container_width=True)

    # Clear Chat for the Current Session
    if st.button("🗑️ Clear Chat"):
        st.session_state[f"memory_{chat_id}"].clear()
        st.session_state[f"messages_{chat_id}"] = []
        st.rerun()

# Chat UI
st.title("AWS Bedrock Chatbot 🤖")
st.markdown(f"### 🆔 Chat ID: `{chat_id[:8]}` (Each chat has a unique session)")

# Chat History Display
chat_container = st.container()
with chat_container:
    for role, content in st.session_state[f"messages_{chat_id}"]:
        if role == "user":
            st.markdown(f'<div style="background-color:#dcf8c6;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color:#f1f0f0;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)

# User Input
user_input = st.text_input("Type your message here...", key="input", on_change=lambda: st.session_state.update({"submitted": True}))

if st.session_state.get("submitted"):
    if user_input.strip():
        # Append user input to chat history
        st.session_state[f"messages_{chat_id}"].append(("user", user_input))

        # Retrieve past chat context
        past_context = st.session_state[f"memory_{chat_id}"].load_memory_variables({}).get("history", "")

        # Fetch Security Guidelines
        security_guidelines = get_security_guidelines()

        # Get AI Response
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context, security_guidelines)

        # Store in Memory
        st.session_state[f"memory_{chat_id}"].save_context({"input": user_input}, {"output": response})

        # Append Bot Response
        st.session_state[f"messages_{chat_id}"].append(("bot", response))

    # Reset Input
    st.session_state["submitted"] = False
    st.rerun()