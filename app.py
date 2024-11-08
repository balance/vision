import streamlit as st
import ollama
from PIL import Image
import os
import logging
import requests

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for UI styling
st.markdown("""
    <style>
        /* Custom styling for the title and description */
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            margin-top: 20px;
        }
        .description {
            font-size: 20px;
            color: #555;
            text-align: center;
            margin-bottom: 20px;
        }
        .response-box {
            background-color: #f4f4f9;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .response-title {
            font-size: 28px;
            color: #4CAF50;
            margin-bottom: 10px;
        }
        .response-text {
            font-size: 18px;
            color: #333;
        }
        .error-message {
            color: #FF4C4C;
            font-size: 18px;
        }
        .info-message {
            font-size: 18px;
            color: #FF9800;
        }
    </style>
""", unsafe_allow_html=True)

# App title and introduction
st.markdown('<div class="title">Nutritional Advisor</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Upload a photo of your dish, and our virtual nutritionist will answer your questions about it.</div>', unsafe_allow_html=True)

# Upload image file
uploaded_file = st.file_uploader("Choose an image of your dish", type=["png", "jpg", "jpeg"])

# Text input for the user's question
user_question = st.text_input("Ask a question about this dish (e.g., 'Is this dish suitable for weight loss?')")

# Check if an image is uploaded and a question is asked
if uploaded_file is not None:
    try:
        logging.debug("Uploaded file received.")

        # Display uploaded image with a caption (using use_container_width instead of use_column_width)
        st.image(uploaded_file, caption="Uploaded Dish Image", use_container_width=True)
        
        # Only proceed if there's a question
        if user_question:
            logging.debug(f"User question received: {user_question}")
            
            # Loading spinner while waiting for the response
            with st.spinner("Analyzing the dish and your question..."):
                # Save the image temporarily
                try:
                    image_path = "/tmp/uploaded_dish.png"
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    logging.debug(f"Image saved to {image_path}")
                except Exception as e:
                    st.error("Failed to save the uploaded image. Please try again.")
                    logging.error(f"Image Save Error: {e}")
                    st.stop()

                # Try sending data to ollama.chat and handle exceptions
                try:
                    logging.debug(f"Sending request to Ollama API with image path: {image_path}")
                    response = ollama.chat(
                        model='llama3.2-vision',
                        messages=[{
                            'role': 'user',
                            'content': user_question,
                            'images': [image_path]
                        }]
                    )
                    
                    logging.debug(f"Ollama API response: {response}")
                    
                    # Clean the response and remove JSON formatting
                    # Assuming response is a string, you can apply further formatting here
                    response_text = response.get("text", response) if isinstance(response, dict) else response
                    
                    # Check for response
                    if response_text:
                        st.markdown('<div class="response-box">', unsafe_allow_html=True)
                        st.markdown('<div class="response-title">Answer to Your Question:</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="response-text">{response_text}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        logging.info(f"Displayed response: {response_text}")
                    else:
                        st.markdown('<div class="response-box">', unsafe_allow_html=True)
                        st.markdown('<div class="response-title">No advice available</div>', unsafe_allow_html=True)
                        st.markdown('<div class="response-text">No advice could be retrieved for this dish. Please try a different image.</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        logging.warning("No advice received from Ollama API.")
                
                except requests.exceptions.ConnectionError:
                    st.markdown('<div class="error-message">There was a problem connecting to the Ollama API. Please check your internet connection.</div>', unsafe_allow_html=True)
                    logging.error("Connection error while trying to connect to Ollama API.")
                except requests.exceptions.Timeout:
                    st.markdown('<div class="error-message">The request to the Ollama API timed out. Please try again later.</div>', unsafe_allow_html=True)
                    logging.error("Ollama API request timed out.")
                except requests.exceptions.RequestException as e:
                    st.markdown('<div class="error-message">An error occurred while making the request to Ollama.</div>', unsafe_allow_html=True)
                    logging.error(f"Request Exception: {e}")
                except Exception as e:
                    st.markdown('<div class="error-message">An unexpected error occurred while processing the request.</div>', unsafe_allow_html=True)
                    logging.error(f"Unexpected Error: {e}")

        else:
            st.markdown('<div class="info-message">Please enter a question about the dish.</div>', unsafe_allow_html=True)
            logging.info("No question entered by the user.")
    
    except Exception as e:
        st.markdown('<div class="error-message">An error occurred while displaying the image. Please try again.</div>', unsafe_allow_html=True)
        logging.error(f"Image Display Error: {e}")
else:
    st.markdown('<div class="info-message">Please upload an image of a dish to ask a question.</div>', unsafe_allow_html=True)
    logging.info("No image uploaded.")
