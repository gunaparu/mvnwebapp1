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
DEFAULT_INSTRUCTIONS = """ 
You are a highly capable AI assistant designed to support developers to guide based on the data provided in the security guidelines.
- Your primary roles and responsibilities include:
    - Providing guidance on security best practices.
    - Analyzing and identifying security risks.
    - Recommending remediation steps.
- You are expected to:
    - Analyze the data provided in the confluence page.
    - Provide guidance based on the data.
    - Identify any security risks.
    - Recommend remediation steps.
- You are not expected to:
    - Access any external data sources.
    - Provide real-time responses.
    - Provide legal advice.
- You can ask for help if you are unsure about any guidance.
- You can provide feedback to improve the quality of your responses.    
- If user asks any question related IAM roles, please ask them whether they are refrering to experian IAM roles or AWS IAM roles.
- If user asks any question related to AWS IAM roles, please provide the information based on the data provided in the security guidelines.
- If user asks any question related to experian IAM roles, please ask for the confirmation whether they are referring to experian IAM roles. If yes provide the information based on the the security guidelines.
- If user asks any question related to AWS IAM roles, please provide the information based on the AWS provided information in the documentation.

"""

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Streamlit Page Config
st.set_page_config(page_title="Armor Gatekeeper 🛡️", page_icon="🚪", layout="wide")
# Chat UI
st.title("Armor Gatekeeper 🛡️")
st.markdown(f"AIG - GateKeeper")

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

# Function to Fetch Security Guidelines from S3
def get_security_guidelines():
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

# Function to Call AWS Bedrock (Claude 3.5) with Security Guidelines & File Context
def get_bedrock_response(prompt, chat_history, file_content):
    # Fetch security guidelines from S3
    security_guidelines = get_security_guidelines()

    # Combine chat history, security guidelines, and file content
    full_prompt = f"""
    Previous Conversation: {chat_history}
    
    Security Guidelines:
    {security_guidelines}

    General Instructions:
    {DEFAULT_INSTRUCTIONS}

    {f"Uploaded File Content:{file_content}" if file_content else ""}

    User Query: {prompt}
    
    Claude:
    """
    
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": full_prompt}],
        "max_tokens": 5000
    }

    # DEBUG: Show Final Prompt Sent to Claude
    st.markdown("### 📝 Claude's Final Prompt:")
    st.json(payload)

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

# Handle File Upload (Only Chat Input)
def handle_uploaded_file(uploaded_file, chat_id):
    if uploaded_file:
        extracted_text = extract_text_from_file(uploaded_file)
        if extracted_text:
            st.session_state[f"uploaded_file_content_{chat_id}"] = extracted_text
            #st.success(f"📄 `{uploaded_file.name}` uploaded successfully!")

# Fetch the latest file content before sending to Claude
file_content = st.session_state.get(f"uploaded_file_content_{chat_id}", "")
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

# Display Chat History
chat_container = st.container()
with chat_container:
    for role, content in st.session_state[f"messages_{chat_id}"]:
        if role == "user":
            st.markdown(f'<div style="background-color:#0078dd;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color:#FIFdfd;padding:10px;border-radius:10px;margin:5px 0;">{content}</div>', unsafe_allow_html=True)
# **New Feature: Chat Input with File Upload Button**

user_input = st.text_input("Type your message here...", key="input", on_change=lambda: st.session_state.update({"submitted": True}))
uploaded_file_chat = st.file_uploader(label ="Upload file", type=["txt", "pdf", "docx"], key="file_uploader", label_visibility="hidden")
# Process Chat Input File Upload
if uploaded_file_chat:
    handle_uploaded_file(uploaded_file_chat, chat_id)
# Process Chat Input
if st.session_state.get("submitted"):
    if user_input.strip():
        st.session_state[f"messages_{chat_id}"].append(("user", user_input))

        past_context = st.session_state[f"memory_{chat_id}"].load_memory_variables({}).get("history", "")

        # Get AI Response
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context, file_content)

        # Store in Memory
        st.session_state[f"memory_{chat_id}"].save_context({"input": user_input}, {"output": response})

        # Append Bot Response
        st.session_state[f"messages_{chat_id}"].append(("bot", response))

    st.session_state["submitted"] = False
    st.rerun()