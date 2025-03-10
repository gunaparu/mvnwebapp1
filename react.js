import React, { useState } from "react";
import axios from "axios";
import { Button, Form, Container, Row, Col } from "react-bootstrap";

const Chatbot = () => {
  const [chatId, setChatId] = useState(localStorage.getItem("chat_id") || generateChatId());
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [file, setFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [loading, setLoading] = useState(false);

  // Generate a unique chat ID if none exists
  const generateChatId = () => {
    const id = Math.random().toString(36).substring(2, 10);
    localStorage.setItem("chat_id", id);
    return id;
  };

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      const reader = new FileReader();
      reader.onload = () => {
        setFileContent(reader.result);
      };
      reader.readAsText(uploadedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    setLoading(true);

    // Append user input to the messages
    const newMessages = [...messages, { role: "user", content: userInput }];
    setMessages(newMessages);
    setUserInput("");

    try {
      const response = await axios.post("http://localhost:5000/chat", {
        chat_id: chatId,
        user_input: userInput,
        file_content: fileContent,
      });
      const botResponse = response.data.message;
      setMessages([...newMessages, { role: "bot", content: botResponse }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages([...newMessages, { role: "bot", content: "Error calling bot." }]);
    }

    setLoading(false);
  };

  return (
    <Container>
      <Row>
        <Col>
          <h2>AWS Bedrock Chatbot 🤖</h2>
          <h4>Chat ID: {chatId}</h4>
          <div className="chat-history">
            {messages.map((msg, index) => (
              <div
                key={index}
                style={{
                  textAlign: msg.role === "user" ? "right" : "left",
                  backgroundColor: msg.role === "user" ? "#dcf8c6" : "#f1f0f0",
                  padding: "10px",
                  borderRadius: "10px",
                  margin: "5px 0",
                }}
              >
                {msg.content}
              </div>
            ))}
          </div>

          <Form onSubmit={handleSubmit}>
            <Form.Group>
              <Form.Control
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Type your message here..."
              />
            </Form.Group>

            <Form.Group>
              <Form.File
                label="Upload File (txt, pdf, docx)"
                onChange={handleFileUpload}
              />
            </Form.Group>

            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? "Thinking..." : "Send"}
            </Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );
};

export default Chatbot;

from flask import Flask, request, jsonify
import boto3
import uuid
import json
import PyPDF2
import docx
from langchain.memory import ConversationBufferMemory

app = Flask(__name__)

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
S3_BUCKET_NAME = "your-security-bucket"
SECURITY_GUIDELINES_FILE = "security_guidelines.txt"

# Initialize AWS Clients
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Function to Extract Text from Uploaded Files
def extract_text_from_file(uploaded_file):
    file_extension = uploaded_file.filename.split(".")[-1].lower()
    
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
    security_guidelines = get_security_guidelines()
    full_prompt = f"""
    Previous Conversation: {chat_history}
    
    Security Guidelines:
    {security_guidelines}

    {f"Uploaded File Content:\n{file_content}" if file_content else ""}

    User Query: {prompt}
    
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

        return response_body.get("content", "Error: Unexpected response format from Claude.")
    except Exception as e:
        return f"Error calling Claude 3.5: {e}"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    chat_id = data.get("chat_id")
    user_input = data.get("user_input")
    file_content = data.get("file_content", "")

    # Fetch the conversation history if needed (for simplicity, using a static memory in this example)
    chat_history = ""

    # Get AI Response
    response = get_bedrock_response(user_input, chat_history, file_content)
    return jsonify({"message": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
    
    
import React, { useState } from "react";
import axios from "axios";
import { Button, Form, Container, Row, Col } from "react-bootstrap";

// Generate a unique chat ID if none exists
const generateChatId = () => {
  const id = Math.random().toString(36).substring(2, 10);
  localStorage.setItem("chat_id", id);
  return id;
};

const Chatbot = () => {
  const [chatId, setChatId] = useState(localStorage.getItem("chat_id") || generateChatId());
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [file, setFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      const reader = new FileReader();
      reader.onload = () => {
        setFileContent(reader.result);
      };
      reader.readAsText(uploadedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    setLoading(true);

    // Append user input to the messages
    const newMessages = [...messages, { role: "user", content: userInput }];
    setMessages(newMessages);
    setUserInput("");

    try {
      const response = await axios.post("http://localhost:5000/chat", {
        chat_id: chatId,
        user_input: userInput,
        file_content: fileContent,
      });
      const botResponse = response.data.message;
      setMessages([...newMessages, { role: "bot", content: botResponse }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages([...newMessages, { role: "bot", content: "Error calling bot." }]);
    }

    setLoading(false);
  };

  return (
    <Container>
      <Row>
        <Col>
          <h2>AWS Bedrock Chatbot 🤖</h2>
          <h4>Chat ID: {chatId}</h4>
          <div className="chat-history">
            {messages.map((msg, index) => (
              <div
                key={index}
                style={{
                  textAlign: msg.role === "user" ? "right" : "left",
                  backgroundColor: msg.role === "user" ? "#dcf8c6" : "#f1f0f0",
                  padding: "10px",
                  borderRadius: "10px",
                  margin: "5px 0",
                }}
              >
                {msg.content}
              </div>
            ))}
          </div>

          <Form onSubmit={handleSubmit}>
            <Form.Group>
              <Form.Control
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Type your message here..."
              />
            </Form.Group>

            <Form.Group>
              <Form.File
                label="Upload File (txt, pdf, docx)"
                onChange={handleFileUpload}
              />
            </Form.Group>

            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? "Thinking..." : "Send"}
            </Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );
};

export default Chatbot;