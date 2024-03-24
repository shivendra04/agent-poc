import os
import streamlit as st
from app import init_rag


def save_pdf(uploaded_file, files_list):
    # Create a folder named "uploaded_data" if it doesn't exist
    save_folder = "uploaded_data"
    os.makedirs(save_folder, exist_ok=True)
    # Save the uploaded PDF file
    output_path = os.path.join(save_folder, uploaded_file.name)
    if output_path in files_list:
        return
    with open(output_path, "wb") as output_file:
        output_file.write(uploaded_file.getbuffer())
    files_list.append(output_path)

files_list = []

def upload_files():
    uploaded_files = st.file_uploader("Choose files", type='pdf', accept_multiple_files=True)
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            save_pdf(uploaded_file, files_list)
        if len(files_list) < 1:
            return
        # Initialize the query engine
        st.session_state.query_engine = init_rag(files_list)
        st.session_state.files_list = files_list

def main():
    # Set the app title 
    st.title('Documents QA App') 
    
    # Add a welcome message 
    st.write('Welcome! Please upload your documents and start quereing')

    # List of options for the select box, including a default placeholder option
    options = ["Select an option", "Upload files"]

    # Create a select box in the sidebar with the placeholder as the default selection
    selected_option = st.sidebar.selectbox(
        label="Choose an option",
        options=options,
        index=0  # Default is the placeholder option
    )

    if "query_engine" not in st.session_state.keys() or selected_option == "Upload files":
        upload_files()
    
    if 'files_list' in st.session_state.keys() and len(st.session_state.files_list) > 0:
        if "messages" not in st.session_state.keys():
            st.session_state.messages = []
        
        if prompt := st.chat_input("Hi! how may I help you?"): # Prompt for user input and save to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            for message in st.session_state.messages: # Display the prior chat messages
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            # If last message is not from assistant, generate a new response
            if st.session_state.messages[-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.query_engine.query(prompt)
                        st.write(response.response)
                        message = {"role": "assistant", "content": response.response}
                        st.session_state.messages.append(message)

if __name__ == '__main__':
    main()
