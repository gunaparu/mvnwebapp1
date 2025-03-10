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