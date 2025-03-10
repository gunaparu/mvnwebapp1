import React, { useState, useRef } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://localhost:5000/chat"; // Update with your backend API

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  // Send Message to Backend (AWS Bedrock)
  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", text: input }];
    setMessages(newMessages);
    setInput("");

    const formData = new FormData();
    formData.append("message", input);
    if (file) formData.append("file", file);

    try {
      const response = await axios.post(API_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const botReply = response.data.reply;
      setMessages([...newMessages, { role: "bot", text: botReply }]);
      setFile(null);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  // Handle File Upload
  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) setFile(uploadedFile);
  };

  return (
    <div className="chat-container">
      <div className="header">
        <h2>Claude Chatbot</h2>
        <button className="new-chat" onClick={() => setMessages([])}>New Chat</button>
      </div>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={msg.role === "user" ? "user-msg" : "bot-msg"}>
            {msg.text}
          </div>
        ))}
      </div>

      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
        />

        <label className="upload-btn" onClick={() => fileInputRef.current.click()}>
          +
        </label>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFileUpload}
        />

        <button className="send-btn" onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;

.chat-container {
  width: 400px;
  margin: 50px auto;
  border: 1px solid #ccc;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #0078ff;
  color: white;
}

.new-chat {
  background: white;
  color: #0078ff;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 5px;
}

.chat-box {
  height: 300px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f9f9f9;
}

.user-msg {
  background-color: #dcf8c6;
  padding: 8px;
  border-radius: 5px;
  margin-bottom: 5px;
  text-align: right;
}

.bot-msg {
  background-color: #f1f0f0;
  padding: 8px;
  border-radius: 5px;
  margin-bottom: 5px;
  text-align: left;
}

.input-container {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: white;
}

.chat-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.upload-btn {
  width: 40px;
  height: 40px;
  background-color: #0078ff;
  color: white;
  text-align: center;
  font-size: 20px;
  line-height: 40px;
  cursor: pointer;
  margin-left: 5px;
  border-radius: 50%;
}

.send-btn {
  padding: 8px 15px;
  margin-left: 5px;
  background-color: #0078ff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}