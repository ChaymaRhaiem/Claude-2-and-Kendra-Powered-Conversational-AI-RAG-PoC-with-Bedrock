# Bedrock Streamlit Chatbot with Claude 2 Integration 🤖


Welcome to the Bedrock Streamlit Chatbot repository, demonstrating a proof of concept developed in November 2023. This project showcases the integration of AWS Bedrock, Claude 2, and Streamlit for advanced document management and conversational AI capabilities.

## Overview 🌟

This proof of concept combines AWS's powerful services with AI capabilities to enable:

- **Document Summarization:** Automatically generates summaries for PDF documents stored in an S3 bucket using AWS Bedrock and the Claude 2.1 model.
- **Conversational AI:** Provides a user-friendly chatbot interface through Streamlit, powered by Claude 2.1. Users can query documents stored in AWS S3 and Kendra.

## Key Technologies Involved 🛠️

- **Streamlit:** A Python library for building interactive web applications.
- **AWS Bedrock:** A managed service designed for deploying and running large language models (LLMs).
- **Anthropic CLAUDE v2:** A powerful LLM from Anthropic AI, capable of generating human-quality text.
- **Amazon S3:** A scalable object storage service for hosting documents.
- **Amazon Kendra:** A service that indexes documents to facilitate efficient search.

## Installation  and Requirements 🚀

1. An AWS account with appropriate permissions for S3, Kendra, and Bedrock.
2. A Kendra index containing the documents you want the chatbot to answer questions about (replace ... with your index ID in doc_summarizer.py).
3. Python 3.x with required libraries (install using pip install -r requirements.txt).



4. Configure environment variables for AWS access:
- Create a `.env` file in the project root.
- Add the following lines, replacing placeholders with your values:

  ```dotenv
  AWS_ACCESS_KEY_ID=<your_access_key>
  AWS_SECRET_ACCESS_KEY=<your_secret_key>
  AWS_DEFAULT_REGION=us-west-2  # Update if your region is different
  S3_BUCKET_NAME=<your_s3_bucket_name>
  ```

Ensure you replace `<your_access_key>`, `<your_secret_key>`, `<your_s3_bucket_name>`, and update `AWS_DEFAULT_REGION` with your actual AWS credentials and S3 bucket information.


Contributing 🤝
Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

License 📄
This project is licensed under the MIT License. See the LICENSE file for more details.

Contact 📧
Email: - rhaiem.chayma@gmail.com
