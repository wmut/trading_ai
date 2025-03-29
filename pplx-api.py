import requests

# Set your API key and endpoint
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.perplexity.ai/chat/completions"

# Define the headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Define the payload for the API request
payload = {
    "model": "mistral-7b-instruct",  # Choose your preferred model
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": False  # Set to True for streaming responses
}

# Make the POST request to the API
response = requests.post(BASE_URL, headers=headers, json=payload)

# Check if the request was successful and print the response
if response.status_code == 200:
    print("Response:", response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")
