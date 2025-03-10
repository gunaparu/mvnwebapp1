import gradio as gr

# Function to process chat and file uploads
def chat_with_bedrock(message, chat_history, file):
    response = f"Claude's response to: {message}"
    
    if file:
        response += f"\n\n(File uploaded: {file})"  # Display file name
    
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": response})
    
    return chat_history, ""

# Function to reset chat
def reset_chat():
    return []

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 AWS Bedrock Claude Chatbot")
    
    with gr.Row():
        new_chat_btn = gr.Button("🆕 New Chat")  # New Chat button
    
    chat_history = gr.Chatbot(label="Claude Chat", type="messages")  # Use OpenAI-style format
    
    with gr.Row():
        msg = gr.Textbox(placeholder="Type your message...", show_label=False)
        file_upload = gr.File(label="", interactive=True, type="filepath", elem_id="hidden-upload")
        submit_btn = gr.Button("Send")
    
    new_chat_btn.click(reset_chat, inputs=[], outputs=[chat_history])  # Reset chat on button click
    submit_btn.click(chat_with_bedrock, inputs=[msg, chat_history, file_upload], outputs=[chat_history, msg])

    # Hide file upload input and show only "+"
    gr.Markdown(
        """
        <style>
            #hidden-upload { display: none !important; }  /* Hide file upload */
            label[for="hidden-upload"]::before {
                content: "+";  /* Display "+" symbol */
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
                color: #0078ff;
                display: inline-block;
                width: 40px;
                height: 40px;
                text-align: center;
                border-radius: 50%;
                border: 2px solid #0078ff;
                line-height: 35px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

demo.launch()