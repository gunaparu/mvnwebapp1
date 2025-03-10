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
S3_BUCKET_NAME = "your-security-bucket"
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

# Initialize Memory
if f"memory_{chat_id}" not in st.session_state:
    st.session_state[f"memory_{chat_id}"] = ConversationBufferMemory()
if f"messages_{chat_id}" not in st.session_state:
    st.session_state[f"messages_{chat_id}"] = []
if f"uploaded_file_content_{chat_id}" not in st.session_state:
    st.session_state[f"uploaded_file_content_{chat_id}"] = ""

# Function to Fetch Security Guidelines
def get_security_guidelines():
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

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

# Function to Call Claude 3.5 with File Context
def get_bedrock_response(prompt, chat_history, security_guidelines, file_content):
    full_prompt = f"""
    Previous Conversation: {chat_history}
    
    User Query: {prompt}
    
    Security Guidelines Reference:
    {security_guidelines}

    Uploaded File Context:
    {file_content}

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

# Chat UI
st.title("AWS Bedrock Chatbot 🤖")
st.markdown(f"### 🆔 Chat ID: `{chat_id[:8]}`")

# Chat History Display
chat_container = st.container()
with chat_container:
    for role, content in st.session_state[f"messages_{chat_id}"]:
        if role == "user":
            st.markdown(f'<div style="background-color:#dcf8c6;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color:#f1f0f0;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)

# **File Upload & Chat Input in One Row**
col1, col2 = st.columns([0.1, 0.9])  

# **( + ) Button for File Upload**
with col1:
    uploaded_file = st.file_uploader("➕", type=["txt", "pdf", "docx"], label_visibility="collapsed")

if uploaded_file:
    extracted_text = extract_text_from_file(uploaded_file)
    st.session_state[f"uploaded_file_content_{chat_id}"] = extracted_text
    st.success(f"📄 `{uploaded_file.name}` uploaded!")

# **Chat Input Box**
with col2:
    user_input = st.text_input("Type your message here...", key="input", on_change=lambda: st.session_state.update({"submitted": True}))

if st.session_state.get("submitted"):
    if user_input.strip():
        st.session_state[f"messages_{chat_id}"].append(("user", user_input))

        # Retrieve chat history
        past_context = st.session_state[f"memory_{chat_id}"].load_memory_variables({}).get("history", "")

        # Fetch Security Guidelines
        security_guidelines = get_security_guidelines()

        # Get File Content (if uploaded)
        file_content = st.session_state[f"uploaded_file_content_{chat_id}"]

        # Get AI Response
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context, security_guidelines, file_content)

        # Store in Memory
        st.session_state[f"memory_{chat_id}"].save_context({"input": user_input}, {"output": response})

        # Append Bot Response
        st.session_state[f"messages_{chat_id}"].append(("bot", response))

    # Reset Input
    st.session_state["submitted"] = False
    st.rerun()