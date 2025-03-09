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


import streamlit as st
import boto3
import json
from langchain.memory import ConversationBufferMemory

# AWS Bedrock Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Set up memory for chat history
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")

# Custom Chat UI
st.markdown(
    """
    <style>
    .chat-container { max-width: 700px; margin: auto; }
    .chat-bubble-user { background-color: #dcf8c6; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 80%; align-self: flex-end; }
    .chat-bubble-bot { background-color: #f1f0f0; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 80%; align-self: flex-start; }
    .message-box { display: flex; flex-direction: column; align-items: flex-start; }
    .message-box.user { align-items: flex-end; }
    </style>
    """,
    unsafe_allow_html=True
)

def get_bedrock_response(prompt, chat_history):
    """Invoke Amazon Bedrock Claude 3.5 model with chat history."""
    full_prompt = chat_history + f"\nUser: {prompt}\nClaude:"

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

chat_history_text = "\n".join(
    [f"{role.capitalize()}: {content}" for role, content in st.session_state.messages]
)

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

        # Retrieve past chat context from LangChain memory
        past_context = st.session_state.memory.load_memory_variables({}).get("history", "")

        # Get response from Claude 3.5 with memory
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context)

        # Append to memory
        st.session_state.memory.save_context({"input": user_input}, {"output": response})

        # Append bot response to chat history
        st.session_state.messages.append(("bot", response))

        # Refresh page to update chat
        st.rerun()


import streamlit as st
import boto3
import json
import os
import markdown
import tempfile
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
from botocore.exceptions import NoCredentialsError
import speech_recognition as sr

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "your-security-guidelines-bucket"
DYNAMODB_TABLE = "ChatHistory"

# Initialize AWS clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

# LangChain memory
memory = ConversationBufferMemory(return_messages=True)

# UI Enhancements
st.set_page_config(page_title="AWS Bedrock Chatbot", layout="wide")

# Dark mode toggle
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")

# Load chat history from DynamoDB
def load_chat_history():
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        response = table.scan()
        return response.get("Items", [])
    except Exception:
        return []

# Save chat history to DynamoDB
def save_chat_history(user_message, ai_message):
    table = dynamodb.Table(DYNAMODB_TABLE)
    table.put_item(Item={"user": user_message, "ai": ai_message})

# Fetch security guidelines from S3
def get_security_guidelines():
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key="security_guidelines.txt")
        return obj["Body"].read().decode("utf-8")
    except NoCredentialsError:
        return "AWS credentials not found."
    except Exception as e:
        return f"Error retrieving security guidelines: {e}"

# Invoke Claude 3.5
def get_bedrock_response(prompt):
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

# Voice input
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError:
            return "Speech recognition service is unavailable."
        except Exception:
            return "Error processing voice input."

# Streamlit UI
st.title("🤖 AWS Bedrock Chatbot")
st.write("Chat with Claude 3.5 Sonnet using Amazon Bedrock!")

# Sidebar for settings
st.sidebar.title("⚙️ Settings")
use_voice = st.sidebar.checkbox("🎤 Enable Voice Input")

# Chat history UI
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Display chat history
for message in st.session_state.messages:
    role, content = message
    if role == "user":
        st.markdown(f"**🧑‍💻 You:** {content}")
    else:
        st.markdown(f"**🤖 Claude 3.5:** {content}")

# User Input
user_input = st.text_input("💬 Type your message here...", key="user_input")

# Handle voice input
if use_voice:
    if st.button("🎤 Speak"):
        user_input = recognize_speech()
        st.session_state.user_input = user_input

if st.button("🚀 Send"):
    if user_input:
        security_data = get_security_guidelines()
        full_prompt = f"{security_data}\n\nUser: {user_input}"
        
        response = get_bedrock_response(full_prompt)

        # Save messages in session and DynamoDB
        st.session_state.messages.append(("user", user_input))
        st.session_state.messages.append(("ai", response))
        save_chat_history(user_input, response)

        # Display response
        st.markdown(f"**🤖 Claude 3.5:** {response}")

        # Clear input field
        st.session_state.user_input = ""
        
        
        
        
        
        


import streamlit as st
import boto3
import json
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "your-security-bucket"  # Update with your S3 bucket name
SECURITY_GUIDELINES_FILE = "security_guidelines.txt"  # Stored in S3

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Initialize LangChain Memory
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

def get_security_guidelines():
    """Retrieve security guidelines from S3."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        guidelines = response["Body"].read().decode("utf-8")
        return guidelines
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

# Streamlit UI Enhancements
st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")
st.markdown("<h1 style='text-align: center;'>AWS Bedrock Chatbot 🤖</h1>", unsafe_allow_html=True)

# Dark Mode Toggle
dark_mode = st.toggle("🌙 Dark Mode")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Collapsible Chat History
with st.expander("📜 Chat History", expanded=False):
    for role, content in st.session_state.messages:
        avatar = "🧑‍💻" if role == "user" else "🤖"
        st.markdown(f"**{avatar} {role.capitalize()}:** {content}")

# User Input
user_input = st.text_input("Type your message here...")

if st.button("Send"):
    if user_input:
        # Retrieve security guidelines from S3
        security_guidelines = get_security_guidelines()

        # Modify prompt to include guidelines
        prompt = f"""
        User Query: {user_input}

        Security Guidelines Reference:
        {security_guidelines}
        """
        
        # Append user input to LangChain memory
        memory.save_context({"input": user_input}, {"output": ""})

        # Get response from Claude 3.5
        response = get_bedrock_response(prompt)

        # Append response to memory
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(response)

        # Update session state for chat history
        st.session_state.messages.append(("user", user_input))
        st.session_state.messages.append(("Claude 3.5", response))

        # Display response with Markdown formatting
        st.markdown(f"**🤖 Claude 3.5:**\n\n{response}")

        # Clear input box after submission
        st.experimental_rerun()
        
        














import streamlit as st
import boto3
import json
from langchain.memory import ConversationBufferMemory

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "your-security-bucket"  # Update with your S3 bucket name
SECURITY_GUIDELINES_FILE = "security_guidelines.txt"  # Stored in S3

# Initialize Bedrock and S3 Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Initialize chat memory in session state
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

# Streamlit UI Enhancements
st.set_page_config(page_title="AWS Bedrock Chatbot", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .chat-container { max-width: 700px; margin: auto; }
    .chat-bubble-user { background-color: #dcf8c6; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 80%; align-self: flex-end; }
    .chat-bubble-bot { background-color: #f1f0f0; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 80%; align-self: flex-start; }
    .message-box { display: flex; flex-direction: column; align-items: flex-start; }
    .message-box.user { align-items: flex-end; }
    </style>
    """,
    unsafe_allow_html=True
)

def get_security_guidelines():
    """Retrieve security guidelines from S3."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=SECURITY_GUIDELINES_FILE)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error fetching security guidelines: {e}"

def get_bedrock_response(prompt, chat_history, security_guidelines):
    """Invoke Amazon Bedrock Claude 3.5 model with chat history and security guidelines."""
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

# Sidebar
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

# Chat History Container
chat_container = st.container()
with chat_container:
    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f'<div class="message-box user"><div class="chat-bubble-user">{content}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-box"><div class="chat-bubble-bot">{content}</div></div>', unsafe_allow_html=True)

# User Input with Enter Key Submission
user_input = st.text_input("Type your message here...", key="input", on_change=lambda: st.session_state.update({"submitted": True}))

if st.session_state.get("submitted"):
    if user_input.strip():
        # Append user input to chat history
        st.session_state.messages.append(("user", user_input))

        # Retrieve past chat context from memory
        past_context = st.session_state.memory.load_memory_variables({}).get("history", "")

        # Fetch security guidelines from S3
        security_guidelines = get_security_guidelines()

        # Get response from Claude 3.5 with memory and security reference
        with st.spinner("Thinking..."):
            response = get_bedrock_response(user_input, past_context, security_guidelines)

        # Save to memory
        st.session_state.memory.save_context({"input": user_input}, {"output": response})

        # Append bot response to chat history
        st.session_state.messages.append(("bot", response))

    # Clear input field after submission
    st.session_state["submitted"] = False
    st.experimental_rerun()
    
def get_bedrock_response(prompt, chat_history, security_guidelines):
    """Invoke Amazon Bedrock Claude 3.5 model with chat history and security guidelines."""
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

        # **Fix: Extract text properly**
        if "content" in response_body and isinstance(response_body["content"], list):
            # Extract text from list of message objects
            extracted_text = "\n".join(
                item["text"] for item in response_body["content"] if isinstance(item, dict) and "text" in item
            )
            return extracted_text if extracted_text else "Error: No valid text in response."

        return "Error: Unexpected response format from Claude."

    except Exception as e:
        return f"Error calling Claude 3.5: {e}"