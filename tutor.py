import streamlit as st
import streamlit.components.v1 as components
import boto3
import json, re

# Set page configuration
st.set_page_config(page_title="Yuzhe's AI Tutor", layout="wide")

st.title("Yuzhe's AI Tutor")
st.write("Ask me any question about Math or Science!")

aws_access_key = st.secrets["database"]["aws_access_key"]
aws_secret_key = st.secrets["database"]["aws_secret_key"]

session = boto3.Session(
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name="us-west-2"
)

# Create Bedrock client
bedrock_runtime = session.client(service_name="bedrock-runtime")

# Function to call Claude via AWS Bedrock
def generate_answer(query):
    try:
        # Claude 3 Sonnet model ID
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        prompt = f"""You are given a query about math or science,
            your task is to output a detailed answer in a single HTML code.
            You should first explain the underlying concepts that are non-specific to the query.
            Then you should explain the query in a step by step manner, as detailed as possible.
            Try to make the answer more aesthetically pleasing for young students.
            Always include fun facts and examples.
            You can use latex to write math equations.
            Query: {query}"""
        
        # Prepare the request payload
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 24000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        # Make API call to Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response["body"].read().decode("utf-8"))
        
        return response_body["content"][0]["text"]
    
    except Exception as e:
        return f"Error: {str(e)}"

# User input
query = st.text_area("", height=150)
submit_button = st.button("Generate Answer")

# Display response
if submit_button and query:
    with st.spinner("Generating Answer..."):
        response = generate_answer(query)

    pattern = r'<html>.*?</html>'
    
    # Use re.DOTALL to ensure '.' matches newline characters as well
    response = re.search(pattern, response, re.DOTALL | re.IGNORECASE).group(0)

    st.subheader("Answer:")
    components.html(response, height=3000)