import streamlit as st
import os
import time
from io import BytesIO
import boto3
from doc_summarizer import Chunk_and_Summarize, handle_user_input, search_documents

os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
os.environ["S3_BUCKET_NAME"] = "bedrockai"
os.environ["AWS_PROFILE"]="default"
# Check if 'messages' exists in session_state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Create a sidebar for navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")  # Add a horizontal line
st.sidebar.header("Pages")
page = st.sidebar.radio("", ["Home", "Chat"])  # Remove the label

st.sidebar.markdown("\n\n\n")  # Add some space

st.sidebar.markdown("---")  # Add a horizontal line

if page == "Home":
    st.title(f"""Document Summarization with Amazon Bedrock""")
    with st.container():
        st.header('Single File Upload')
        File = st.file_uploader('Upload a file', type=["pdf"], key="new")
        if File is not None:
            s3_bucket = os.environ.get("S3_BUCKET_NAME")
            aws_region = os.environ.get("AWS_REGION")
            s3 = boto3.client("s3", region_name=aws_region)

            s3_key = f"Input/{File.name}"
            s3.upload_fileobj(File, s3_bucket, s3_key)

            st.success(f'File {File.name} is successfully uploaded to S3!')
            start = time.time()

            file_bytes = BytesIO()
            s3.download_fileobj(s3_bucket, s3_key, file_bytes)

            st.write(Chunk_and_Summarize(file_bytes))

            end = time.time()
            seconds = int(((end - start) % 60))
            minutes = int((end - start) // 60)
            total_time = f"""Time taken to generate a summary:
            Minutes: {minutes} Seconds: {round(seconds, 2)}"""
            with st.sidebar:
                st.header(total_time)

elif page == "Chat":
    st.header('Chatbot')

    # Create a new input field
    with st.form(key='chat_form'):
        user_input = st.text_input("Enter your message:", key='user_input')
        submit_button = st.form_submit_button(label='Submit')
    
        if submit_button:
            response = handle_user_input(user_input)
        
            # Append user message and assistant response to messages
            st.session_state['messages'].append(("User", user_input))
            st.session_state['messages'].append(("Assistant", response))
        
            # Rerun the script
            st.experimental_rerun()

    # Display all messages in reverse order
    for index, (author, message) in enumerate(reversed(st.session_state['messages'])):
        if author == "User":
            st.text_area(f"{author} ", message)
        elif author == "Assistant":
            st.text_area(f"{author} ", message)