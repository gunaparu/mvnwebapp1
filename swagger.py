import streamlit as st
import boto3
import json
import time
from langchain.memory import ConversationBufferMemory

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "your-security-bucket"  # Update with your S3 bucket name
SECURITY_GUIDELINES_FILE = "security_guidelines.txt"
DYNAMODB_TABLE = "chatbot_history"

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb_client = boto3.client("dynamodb", region_name=AWS_REGION)

# Initialize chat memory in session state
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

# Streamlit UI Enhancements
st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")

# Dark Mode Toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Custom CSS for Light & Dark Mode
dark_mode_css = """
    <style>
    body { background-color: #222; color: #ddd; }
    .chat-bubble-user { background-color: #4caf50; color: white; }
    .chat-bubble-bot { background-color: #444; color: white; }
    </style>
"""
light_mode_css = """
    <style>
    body { background-color: #fff; color: #000; }
    .chat-bubble-user { background-color: #dcf8c6; color: black; }
    .chat-bubble-bot { background-color: #f1f0f0; color: black; }
    </style>
"""
st.markdown(dark_mode_css if st.session_state.dark_mode else light_mode_css, unsafe_allow_html=True)

# Function to retrieve security guidelines
def get_security_guidelines():
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

# Function to get Claude response
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
        
        # Extract text properly
        if "content" in response_body and isinstance(response_body["content"], list):
            extracted_text = "\n".join(item["text"] for item in response_body["content"] if isinstance(item, dict) and "text" in item)
            return extracted_text if extracted_text else "Error: No valid text in response."

        return "Error: Unexpected response format from Claude."

    except Exception as e:
        return f"Error calling Claude 3.5: {e}"

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
    except Exception as e:
        st.error(f"Error storing chat history: {e}")

# Sidebar
with st.sidebar:
    st.header("🤖 Chatbot Settings")
    
    if st.button("🌙 Toggle Dark Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.experimental_rerun()

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

# Chat History Container
chat_container = st.container()
with chat_container:
    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-bot">{content}</div>', unsafe_allow_html=True)

# Quick Response Buttons
faq_responses = ["What are AWS IAM best practices?", "How does AWS KMS work?", "Explain AWS security monitoring."]
st.markdown("**Quick Questions:**")
cols = st.columns(len(faq_responses))
for i, question in enumerate(faq_responses):
    if cols[i].button(question):
        st.session_state["input"] = question
        st.session_state["submitted"] = True

# User Input
user_input = st.text_input("Type your message here...", key="input")

if user_input.strip():
    st.session_state.messages.append(("user", user_input))
    
    # Retrieve past chat context
    past_context = st.session_state.memory.load_memory_variables({}).get("history", "")

    # Fetch security guidelines
    security_guidelines = get_security_guidelines()

    # Get AI response
    with st.spinner("Thinking..."):
        response = get_bedrock_response(user_input, past_context, security_guidelines)

    # Save chat history
    st.session_state.memory.save_context({"input": user_input}, {"output": response})
    store_chat_history(user_input, response)

    # Append bot response to chat history
    st.session_state.messages.append(("bot", response))

    st.experimental_rerun()