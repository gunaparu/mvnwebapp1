import streamlit as st
import boto3
import json
import uuid
import requests
import html2text  # Convert HTML to Markdown
from langchain.memory import ConversationBufferMemory

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Confluence Configuration
CONFLUENCE_BASE_URL = "https://your-company.atlassian.net/wiki/rest/api/content"
CONFLUENCE_PAGE_ID = "123456789"  # Replace with your page ID
CONFLUENCE_API_TOKEN = "your-api-token"  # Use API token for authentication

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

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

# Function to Fetch and Convert Security Guidelines from Confluence
def get_security_guidelines():
    try:
        url = f"{CONFLUENCE_BASE_URL}/{CONFLUENCE_PAGE_ID}?expand=body.storage"
        headers = {
            "Authorization": f"Bearer {CONFLUENCE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for non-200 responses

        data = response.json()
        html_content = data["body"]["storage"]["value"]  # Get HTML content

        # Convert HTML to Markdown
        markdown_content = html2text.html2text(html_content)
        return markdown_content.strip()

    except requests.exceptions.RequestException as e:
        return f"Error fetching security guidelines from Confluence: {e}"

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
    new_chat_id = str(uuid.uuid4())
    new_chat_url = f"{st.get_option('server.baseUrlPath')}?chat_id={new_chat_id}"
    st.link_button("➕ New Chat", new_chat_url, use_container_width=True)

    if st.button("🗑️ Clear Chat"):
        st.session_state[f"memory_{chat_id}"].clear()
        st.session_state[f"messages_{chat_id}"] = []
        st.rerun()

# Chat UI
st.title("AWS Bedrock Chatbot 🤖")
st.markdown(f"### 🆔 Chat ID: `{chat_id[:8]}`")

chat_container = st.container()
with chat_container:
    for role, content in st.session_state[f"messages_{chat_id}"]:
        if role == "user":
            st.markdown(f"**User:** {content}", unsafe_allow_html=True)
        else:
            st.markdown(f"**Claude:** {content}", unsafe_allow_html=True)

user_input = st.text_input("Type your message here...", key="input", on_change=lambda: st.session_state.update({"submitted": True}))

if st.session_state.get("submitted"):
    if user_input.strip():
        st.session_state[f"messages_{chat_id}"].append(("user", user_input))

        past_context = st.session_state[f"memory_{chat_id}"].load_memory_variables({}).get("history", "")

        # Fetch Security Guidelines from Confluence
        security_guidelines = get_security_guidelines()

        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context, security_guidelines)

        st.session_state[f"memory_{chat_id}"].save_context({"input": user_input}, {"output": response})
        st.session_state[f"messages_{chat_id}"].append(("bot", response))

    st.session_state["submitted"] = False
    st.rerun()