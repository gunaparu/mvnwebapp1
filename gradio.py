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
        gr.Markdown("# 🤖 AWS Bedrock Claude Chatbot")  # ❌ Removed scale=8
        new_chat_btn = gr.Button("🆕 New Chat", size="sm")  # New Chat on top right

    chat_history = gr.Chatbot(label="Claude Chat", type="messages")  # OpenAI-style format
    
    with gr.Row():
        msg = gr.Textbox(placeholder="Type your message...", show_label=False, scale=7)
        upload_btn = gr.Button("+", scale=1, size="sm")  # "+" Upload Button
        file_upload = gr.File(label="", type="filepath", visible=False)  # Hidden File Upload
        submit_btn = gr.Button("Send", scale=1, size="sm")  # Smaller Send button
    
    new_chat_btn.click(reset_chat, inputs=[], outputs=[chat_history])  # Reset chat on button click
    submit_btn.click(chat_with_bedrock, inputs=[msg, chat_history, file_upload], outputs=[chat_history, msg])
    upload_btn.click(lambda: None, [], [], _js="document.getElementById('file-upload-input').click()")  # JS to trigger upload

    # Inject JavaScript for triggering file upload
    gr.HTML(
        """
        <input type="file" id="file-upload-input" style="display:none;">
        """
    )

demo.launch()