import streamlit as st
import boto3
import json
import uuid
import PyPDF2
import docx
from langchain.memory import ConversationBufferMemory

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "securityguidelines"
SECURITY_GUIDELINES_FILE = "security_guidelines.txt"

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Streamlit Page Config
st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")

# Handle Unique Chat Sessions
query_params = st.query_params
chat_id = query_params.get("chat_id", str(uuid.uuid4()))
st.query_params["chat_id"] = chat_id  

# Initialize Memory for the Chat Session
if f"memory_{chat_id}" not in st.session_state:
    st.session_state[f"memory_{chat_id}"] = ConversationBufferMemory()
if f"messages_{chat_id}" not in st.session_state:
    st.session_state[f"messages_{chat_id}"] = []
if f"uploaded_file_content_{chat_id}" not in st.session_state:
    st.session_state[f"uploaded_file_content_{chat_id}"] = ""

# Function to Extract Text from Uploaded Files
def extract_text_from_file(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "txt":
        return uploaded_file.read().decode("utf-8")
    elif file_extension == "pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file_extension == "docx":
        doc = docx.Document(uploaded_file)
        return " ".join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file type."
def get_security_guidelines():
    """Retrieve security guidelines from S3."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

# Function to Call AWS Bedrock (Claude 3.5) with File Context
def get_bedrock_response(prompt, chat_history, file_content,security_guidelines):
    full_prompt = f"""
    Previous Conversation: {chat_history}
    
    User Query: {prompt}

    Uploaded File Context:
    {file_content}

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

        if isinstance(response_body.get("content"), list):
            return " ".join([item.get("text", "") for item in response_body["content"] if isinstance(item, dict)])
        elif isinstance(response_body.get("content"), str):
            return response_body["content"]
        else:
            return "Error: Unexpected response format from Claude."
    except Exception as e:
        return f"Error calling Claude 3.5: {e}"

# Sidebar Controls
with st.sidebar:
    st.header("🤖 Chatbot Settings")

    # New Chat Button
    new_chat_id = str(uuid.uuid4())
    new_chat_url = f"{st.get_option('server.baseUrlPath')}?chat_id={new_chat_id}"
    st.link_button("➕ New Chat", new_chat_url, use_container_width=True)

    # Clear Chat
    if st.button("🗑️ Clear Chat"):
        st.session_state[f"memory_{chat_id}"].clear()
        st.session_state[f"messages_{chat_id}"] = []
        st.session_state[f"uploaded_file_content_{chat_id}"] = ""
        st.rerun()

# Chat UI
st.title("AWS Bedrock Chatbot 🤖")
st.markdown(f"### 🆔 Chat ID: `{chat_id[:8]}` (Unique Session)")

# Display Chat History
chat_container = st.container()
with chat_container:
    for role, content in st.session_state[f"messages_{chat_id}"]:
        if role == "user":
            st.markdown(f'<div style="background-color:#0078dd;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color:#FIFdfd;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)

# **New Feature: Chat Input with File Upload Button**
col1, col2 = st.columns([8, 1])  

with col1:
    user_input = st.text_input("Type your message here...", key="input", on_change=lambda: st.session_state.update({"submitted": True}))

with col2:
    uploaded_file_chat = st.file_uploader("➕", type=["txt", "pdf", "docx"], label_visibility="collapsed")

# Process File Upload Beside Chat
if uploaded_file_chat:
    extracted_text = extract_text_from_file(uploaded_file_chat)
    st.session_state[f"uploaded_file_content_{chat_id}"] = extracted_text
    st.success(f"📄 `{uploaded_file_chat.name}` uploaded!")

# Process Chat Input
if st.session_state.get("submitted"):
    if user_input.strip():
        st.session_state[f"messages_{chat_id}"].append(("user", user_input))

        past_context = st.session_state[f"memory_{chat_id}"].load_memory_variables({}).get("history", "")

        file_content = st.session_state[f"uploaded_file_content_{chat_id}"]
        security_guidelines = get_security_guidelines()
        extracted_text = extract_text_from_file(uploaded_file_chat)
        # Get AI Response
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context, extracted_text, security_guidelines)

        # Store in Memory
        st.session_state[f"memory_{chat_id}"].save_context({"input": user_input}, {"output": response})

        # Append Bot Response
        st.session_state[f"messages_{chat_id}"].append(("bot", response))

    st.session_state["submitted"] = False
    st.rerun()