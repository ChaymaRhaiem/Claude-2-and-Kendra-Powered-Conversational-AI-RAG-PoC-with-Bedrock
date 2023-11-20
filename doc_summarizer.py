import boto3
import json
from dotenv import load_dotenv
import tiktoken
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
import os
from datetime import datetime 
import botocore.config

os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
os.environ["S3_BUCKET_NAME"] = "bedrockai"
os.environ["AWS_PROFILE"]="default"

load_dotenv()
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
config = botocore.config.Config(connect_timeout=120, read_timeout=120)

boto3.setup_default_session(profile_name=os.getenv("default"))
bedrock = boto3.client('bedrock-runtime', 'us-west-2', endpoint_url='https://bedrock-runtime.us-west-2.amazonaws.com', config=config)
kendra = boto3.client('kendra')

def summarizer(prompt_data) -> str:
    # Format the prompt data
    formatted_prompt = f"Human: {prompt_data}\nAssistant:"

    body = json.dumps({
        "prompt": formatted_prompt,
        "max_tokens_to_sample": 8191,
        "temperature": 0,
        "top_k": 250,
        "top_p": 0.5,
        "stop_sequences": []
    })
    response = bedrock.invoke_model(
        body=body,
        modelId='anthropic.claude-v2',
        accept='application/json',
        contentType='application/json'
    )
    response_body = json.loads(response.get('body').read())
    answer = response_body.get('completion')
    return answer



def num_tokens_from_string(string) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def Chunk_and_Summarize(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    texts = text_splitter.create_documents([text])
    summary = ""
    for index, chunk in enumerate(texts):
        chunk_content = chunk.page_content
        prompt = f"Provide a detailed summary for the chunk of text provided:\n{chunk_content}\n\n"
        summary += summarizer(prompt)
        print(f"Number of tokens for Chunk {index + 1} with the prompt: {num_tokens_from_string(prompt)} tokens")
        print("-------------------------------------------------------------------------------------------------------")

    final_summary_prompt = f"You will be given a set of summaries. Create a cohesive summary from the provided individual summaries.\nSummaries:\n{summary}\n\n"
    print(f"Number of tokens for this Chunk with the final prompt: {num_tokens_from_string(final_summary_prompt)}")
    return summarizer(final_summary_prompt)

def search_documents(query):
    index_id = '423e4538-ec87-4d2a-8795-04279a355286'  # Replace with your Kendra Index ID
    response = kendra.query(
        IndexId=index_id,
        QueryText=query
    )
    return response

def answer_question_with_bedrock(query, search_results):
    # Extract relevant information from Kendra search results
    documents = search_results.get('ResultItems', [])
    document_texts = [document.get('DocumentExcerpt', {}).get('Text', '') for document in documents]
    data = "\n".join(document_texts)

    # Ensure the prompt ends with "Assistant:"
    if not data.endswith("Assistant:"):
        data += "\nAssistant:"

    formatted_query = f"\n\nHuman: {query}\n{data}"

    body = json.dumps({
        "prompt": formatted_query,
        "max_tokens_to_sample": 8191,
        "temperature": 0,
        "top_k": 250,
        "top_p": 0.5,
        "stop_sequences": []
    })

    try:
        response = bedrock.invoke_model(
            body=body,
            modelId='anthropic.claude-v2',
            accept='application/json',
            contentType='application/json'
        )
    except botocore.exceptions.BotoCoreError as e:
        print(f"An error occurred while invoking the model: {e}")
        return None

    response_body = json.loads(response.get('body').read())
    answer = response_body.get('completion')
    return answer




def handle_user_input(user_input, conversation_history=None):
    if not user_input.strip():
        return "I'm sorry, but I didn't receive any input. Could you please provide more information?"
    # Initialize conversation_history if it's None
    if conversation_history is None:
        conversation_history = []
    
    # Append user input to conversation history
    conversation_history.append({"role": "user", "content": user_input})
    
    formatted_input = f"Human: {user_input}\nAssistant:"
    tokens = word_tokenize(formatted_input)
    pos_tags = pos_tag(tokens)
    named_entities = ne_chunk(pos_tags)
    search_results = search_documents(user_input)
    response = answer_question_with_bedrock(user_input, search_results)
    
    # Append assistant response to conversation history
    conversation_history.append({"role": "assistant", "content": response})
    
    # Convert conversation_history to JSON and upload to S3
    s3_bucket = os.environ.get("S3_BUCKET_NAME")
    aws_region = os.environ.get("AWS_REGION")
    s3 = boto3.client("s3", region_name=aws_region)
    
    # Get current date and time
    now = datetime.now()
    date_time = now.strftime("%Y%m%d_%H%M%S")
    
    # Use the current date and time in the S3 key
    s3_key = f"History/conversation_{date_time}.json"
    s3.put_object(Body=json.dumps(conversation_history), Bucket=s3_bucket, Key=s3_key)
    
    return response