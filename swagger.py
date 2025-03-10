import streamlit as st
import boto3
import json
import time
from langchain.memory import ConversationBufferMemory

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "your-security-bucket"  # Replace with your S3 bucket name
SECURITY_GUIDELINES_FILE = "security_guidelines.txt"
DYNAMODB_TABLE = "chatbot_history"

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb_client = boto3.client("dynamodb", region_name=AWS_REGION)

# Initialize LangChain Memory
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

# Streamlit UI Configuration
st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")

# Custom Styling for Chat UI
st.markdown(
    """
    <style>
    .chat-container { max-width: 700px; margin: auto; }
    .chat-bubble-user { background-color: #dcf8c6; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 80%; align-self: flex-end; }
    .chat-bubble-bot { background-color: #f1f0f0; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 80%; align-self: flex-start; }
    .message-box { display: flex; flex-direction: column; align-items: flex-start; }
    .message-box.user { align-items: flex-end; }
    .input-container { display: flex; align-items: center; }
    .upload-button { background-color: transparent; border: none; font-size: 24px; cursor: pointer; margin-left: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to fetch security guidelines from S3
def get_security_guidelines():
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

# Function to store chat history in DynamoDB
def store_chat_history(user_input, bot_response):
    timestamp = int(time.time())
    try:
        dynamodb_client.put_item(
            TableName=DYNAMODB_TABLE,
            Item={
                "timestamp": {"N": str(timestamp)},
                "user_input": {"S": user_input},
                "bot_response": {"S": bot_response}
            }
        )
    except dynamodb_client.exceptions.ResourceNotFoundException:
        st.error("Error: DynamoDB table 'chatbot_history' not found. Please create it.")
    except Exception as e:
        st.error(f"Error storing chat history: {e}")

# Function to call AWS Bedrock Claude 3.5
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

        if "content" in response_body and isinstance(response_body["content"], list):
            return response_body["content"][0].get("text", "Error: No response text.")
        return "Error: Unexpected response format."
    except Exception as e:
        return f"Error calling Claude 3.5: {e}"

# Sidebar Settings
with st.sidebar:
    st.header("🤖 Chatbot Settings")
    if st.button("🗑️ Clear Chat"):
        st.session_state.memory.clear()
        st.session_state.messages = []
        st.rerun()

# Chat UI
st.title("AWS Bedrock Chatbot 🤖")
st.markdown("### 💬 Chat with AI")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
chat_container = st.container()
with chat_container:
    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f'<div class="message-box user"><div class="chat-bubble-user">{content}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-box"><div class="chat-bubble-bot">{content}</div></div>', unsafe_allow_html=True)

# Layout for Input Box + Upload Button
col1, col2 = st.columns([8, 1])

with col1:
    user_input = st.text_input("Type your message here...", key="input", on_change=lambda: st.session_state.update({"submitted": True}))

with col2:
    uploaded_file = st.file_uploader("", label_visibility="collapsed", type=["txt", "pdf", "docx"])

# Handle Input Submission
if st.session_state.get("submitted"):
    if user_input.strip():
        st.session_state.messages.append(("user", user_input))

        past_context = st.session_state.memory.load_memory_variables({}).get("history", "")
        security_guidelines = get_security_guidelines()

        # Call Bedrock AI
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context, security_guidelines)

        # Store Chat History in DynamoDB
        store_chat_history(user_input, response)

        # Save to memory
        st.session_state.memory.save_context({"input": user_input}, {"output": response})

        # Append bot response to chat history
        st.session_state.messages.append(("bot", response))

    st.session_state["submitted"] = False
    st.experimental_rerun()