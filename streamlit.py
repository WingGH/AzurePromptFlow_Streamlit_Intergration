import streamlit as st
import urllib.request
import json
import os
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AZURE_ENDPOINT_KEY = os.getenv("AZURE_ENDPOINT_KEY")  # Fetch the Azure key from environment variables for secure access

def allow_self_signed_https(allowed):
    """
    Bypass the server certificate verification on the client side.
    This is useful for development environments with self-signed certificates.
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

# Streamlit UI setup
st.title('Welcome to Company XXX AI Assistant!')
st.sidebar.title("Your AI-Powered Copilot")
st.sidebar.caption("Enhancing Learning with AI")
st.sidebar.info("""
Generative AI technology can revolutionize multiple industries, particularly in education,
by offering detailed and interactive insights into complex topics. Whether you're exploring
healthcare, finance, or general knowledge, this assistant is here to help.
""")

def main():
    """
    Main function to handle chat interactions and API communication.
    """
    allow_self_signed_https(True)  # Enable self-signed HTTPS certificates (only for development purposes)

    # Initialize chat history if not already present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for interaction in st.session_state.chat_history:
        if interaction["inputs"]["chat_input"]:
            with st.chat_message("user"):
                st.write(interaction["inputs"]["chat_input"])
        if interaction["outputs"]["chat_output"]:
            with st.chat_message("assistant"):
                st.write(interaction["outputs"]["chat_output"])

    # Handle user input
    if user_input := st.chat_input("Ask me anything..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)

        # Prepare data for API request
        data = {"chat_history": st.session_state.chat_history, 'chat_input': user_input}
        body = json.dumps(data).encode('utf-8')

        # Define Azure ML endpoint URL and headers
        url = 'https://your-azure-endpoint-url.com/score'  # Replace with your Azure endpoint URL
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AZURE_ENDPOINT_KEY}',  # Use secure key
            'azureml-model-deployment': 'your-model-deployment-name'  # Replace with your deployment name
        }

        # Make API request
        req = urllib.request.Request(url, body, headers)
        try:
            response = urllib.request.urlopen(req)
            response_data = json.loads(response.read().decode('utf-8'))

            # Check if 'chat_output' exists in the response data
            if 'chat_output' in response_data:
                with st.chat_message("assistant"):
                    st.markdown(response_data['chat_output'])

                # Append the interaction to the chat history
                st.session_state.chat_history.append(
                    {"inputs": {"chat_input": user_input},
                     "outputs": {"chat_output": response_data['chat_output']}}
                )
            else:
                st.error("The response data does not contain a 'chat_output' key.")
        except urllib.error.HTTPError as error:
            st.error(f"The request failed with status code: {error.code}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
