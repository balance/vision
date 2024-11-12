import streamlit as st
from PIL import Image
import requests
import json

# Set up the Ollama endpoint
OLLAMA_API_URL = "http://localhost:8501/api/analyze"  # Replace with your actual Ollama API endpoint if different

# Streamlit interface
st.title("Image Analysis with Ollama")

st.write("Upload an image and provide a prompt for analysis.")

# File upload for the image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Text input for the user's prompt
user_prompt = st.text_input("Describe what you want to analyze about the image")

# Display the uploaded image
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
else:
    st.write("Please upload an image.")

# Analyze button
if uploaded_file and user_prompt:
    if st.button("Analyze Image"):
        # Convert image to base64 or another suitable format (for demonstration, assume it's converted properly)
        image_data = uploaded_file.read()
        
        # Prepare payload for the Ollama API
        payload = {
            "prompt": user_prompt,
            "image_data": image_data  # Ensure image data is properly encoded
        }
        
        # Send request to Ollama
        try:
            response = requests.post(OLLAMA_API_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
            response_data = response.json()
            
            if response.status_code == 200:
                analysis = response_data.get("analysis", "No analysis available.")
                st.write("**Analysis Result:**", analysis)
            else:
                st.write("Failed to analyze the image. Please try again.")
        except Exception as e:
            st.write("An error occurred while analyzing the image:", e)
