import streamlit as st
import ollama
from PIL import Image

# App title and introduction
st.title("Nutritional Advisor")
st.write("Upload a photo of your dish, and our virtual nutritionist will answer your questions about it.")

# Upload image file
uploaded_file = st.file_uploader("Choose an image of your dish", type=["png", "jpg", "jpeg"])

# Text input for the user's question
user_question = st.text_input("Ask a question about this dish (e.g., 'Is this dish suitable for weight loss?')")

if uploaded_file is not None:
    # Display uploaded image with a caption
    st.image(uploaded_file, caption="Uploaded Dish Image", use_column_width=True)
    
    # Only proceed if there's a question
    if user_question:
        # Loading spinner while waiting for the response
        with st.spinner("Analyzing the dish and your question..."):
            # Save the image temporarily
            image_path = "/tmp/uploaded_dish.png"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

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
                
                # Display the response in a styled box if available
                if response:
                    st.markdown("### Answer to Your Question")
                    st.success(response, icon="🍽️")
                else:
                    st.warning("No advice could be retrieved for this dish. Please try a different image.")
            
            except Exception as e:
                st.error("An error occurred while analyzing the dish. Please try again.")
                st.write(f"Error details: {e}")  # Optional: Display error details for debugging
    else:
        st.info("Please enter a question about the dish.")
else:
    st.info("Please upload an image of a dish to ask a question.")