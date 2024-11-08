import streamlit as st
import ollama
from PIL import Image
import logging
import os

# Set up logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# App title and introduction
st.title("Nutritional Advisor")
st.write("Upload a photo of your dish, and our virtual nutritionist will answer your questions about it.")

# Upload image file
uploaded_file = st.file_uploader("Choose an image of your dish", type=["png", "jpg", "jpeg"])

# Text input for the user's question
user_question = st.text_input("Ask a question about this dish (e.g., 'Is this dish suitable for weight loss?')")

# Process the uploaded file and user question if provided
if uploaded_file is not None:
    # Display uploaded image with a caption, using use_container_width instead of use_column_width
    st.image(uploaded_file, caption="Uploaded Dish Image", use_container_width=True)
    logging.info("User uploaded an image successfully.")

    # Only proceed if there's a question
    if user_question:
        logging.info(f"User asked a question: {user_question}")
        # Loading spinner while waiting for the response
        with st.spinner("Analyzing the dish and your question..."):
            # Save the image temporarily
            try:
                image_path = "/tmp/uploaded_dish.png"
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                logging.info("Image saved successfully at /tmp/uploaded_dish.png.")
            except IOError as io_err:
                st.error("An error occurred while saving the uploaded image.")
                logging.error(f"Failed to save uploaded image: {io_err}")
            except Exception as save_err:
                st.error("An unexpected error occurred while handling the image.")
                logging.exception("Unexpected error during image save.")

            # Try sending data to ollama.chat and handle exceptions
            try:
                response = ollama.chat(
                    model='llama3.2-vision',
                    messages=[{
                        'role': 'user',
                        'content': user_question,
                        'images': [image_path]
                    }]
                )
                logging.info("Successfully received response from ollama model.")

                # Display the response in a styled box if available
                if response:
                    response_text = response.get("text", response) if isinstance(response, dict) else response
                    st.markdown("### Answer to Your Question")
                    st.success(response_text, icon="🍽️")
                else:
                    st.warning("No advice could be retrieved for this dish. Please try a different image.")
                    logging.warning("Empty response received from ollama model.")

            except ollama.exceptions.ConnectionError as conn_err:
                st.error("Failed to connect to the analysis service. Please check your connection.")
                logging.error(f"ConnectionError while accessing ollama API: {conn_err}")

            except ollama.exceptions.APIError as api_err:
                st.error("The analysis service encountered an error. Please try again later.")
                logging.error(f"APIError from ollama API: {api_err}")

            except Exception as e:
                st.error("An unexpected error occurred while analyzing the dish. Please try again.")
                logging.exception("Unexpected error during ollama chat API call.")

            finally:
                # Clean up the temporary file after processing
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logging.info("Temporary image file deleted successfully.")
                except Exception as cleanup_err:
                    logging.warning(f"Failed to delete temporary image file: {cleanup_err}")

    else:
        st.info("Please enter a question about the dish.")
        logging.info("No question provided by the user.")

else:
    st.info("Please upload an image of a dish to ask a question.")
    logging.info("No image uploaded by the user.")
