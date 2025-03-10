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