import gradio as gr

# Function to handle chat
def chat_with_bedrock(message, chat_history, file):
    response = f"Claude's response to: {message}"
    
    if file:
        response += f"\n\n(File uploaded: {file.name})"  # Display file name
    
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": response})
    
    return chat_history, ""

# Function to reset chat
def reset_chat():
    return []

# Gradio UI
with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# 🤖 AWS Bedrock Claude Chatbot")
        new_chat_btn = gr.Button("🆕 New Chat", scale=0, size="sm")  # Move New Chat to top right

    chat_history = gr.Chatbot(label="Claude Chat", type="messages")  # OpenAI-style format
    
    with gr.Row():
        msg = gr.Textbox(placeholder="Type your message...", show_label=False, scale=8)
        file_upload = gr.File(label="", type="filepath", elem_id="hidden-upload", scale=0)
        submit_btn = gr.Button("Send", scale=1, size="sm")  # Smaller Send button
    
    new_chat_btn.click(reset_chat, inputs=[], outputs=[chat_history])  # Reset chat on button click
    submit_btn.click(chat_with_bedrock, inputs=[msg, chat_history, file_upload], outputs=[chat_history, msg])

    # Hide file upload input and show only "+"
    gr.HTML(
        """
        <style>
            #hidden-upload { display: none !important; }  /* Hide file upload */
            label[for="hidden-upload"]::before {
                content: "+";  /* Display "+" symbol */
                font-size: 30px;
                font-weight: bold;
                cursor: pointer;
                color: #0078ff;
                display: inline-block;
                width: 30px;
                height: 30px;
                text-align: center;
                border-radius: 50%;
                border: 2px solid #0078ff;
                line-height: 25px;
            }
        </style>
        """
    )

demo.launch()