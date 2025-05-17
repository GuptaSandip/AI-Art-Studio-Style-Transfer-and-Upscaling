import streamlit as st
import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
from PIL import Image
import torch
# from realesrgan import RealESRGAN
from py_real_esrgan.model import RealESRGAN
import io

# Load the style transfer model
@st.cache_resource
def load_style_model():
    return hub.load("https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2")

style_model = load_style_model()

# Initialize the ESRGAN model
@st.cache_resource
def load_esrgan_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = RealESRGAN(device, scale=4)
    model.load_weights('weights/RealESRGAN_x4.pth', download=True)
    return model

esrgan_model = load_esrgan_model()

def preprocess_image(image):
    image = image.resize((256, 256))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image.astype(np.float32)

def upscale_image(image):
    image = Image.fromarray(image)
    upscaled_image = esrgan_model.predict(image)
    return upscaled_image

# def save_image_to_buffer(image_array, format="PNG"):
#     pil_image = Image.fromarray(image_array)
#     buffer = io.BytesIO()
#     pil_image.save(buffer, format=format)
#     buffer.seek(0)
#     return buffer

def save_image_to_buffer(image, format="PNG"):
    """Convert image to in-memory buffer."""
    if isinstance(image, np.ndarray):
        # Convert numpy array to PIL Image if needed
        image = Image.fromarray(image)
    
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer



def main():
    st.title("AI Art Studio: Style Transfer & Upscaling")

    st.sidebar.header("Upload Images")
    content_image = st.sidebar.file_uploader("Upload Content Image", type=["jpg", "png"])
    style_image = st.sidebar.file_uploader("Upload Style Image", type=["jpg", "png"])

    if content_image and style_image:
        content_image = Image.open(content_image)
        style_image = Image.open(style_image)

        st.image(content_image, caption="Content Image", use_column_width=True)
        st.image(style_image, caption="Style Image", use_column_width=True)

        content_array = preprocess_image(content_image)
        style_array = preprocess_image(style_image)

        stylized_image = style_model(tf.constant(content_array), tf.constant(style_array))[0]
        stylized_image = np.squeeze(stylized_image)
        stylized_image = np.clip(stylized_image, 0.0, 1.0)
        stylized_image = (stylized_image * 255).astype(np.uint8)

        st.image(stylized_image, caption="Stylized Image", use_column_width=True)

        if st.button("Upscale Image"):
            upscaled_image = upscale_image(stylized_image)
            st.image(upscaled_image, caption="Upscaled Image", use_column_width=True)

            # Provide download links for both images
            stylized_buffer = save_image_to_buffer(stylized_image)
            upscaled_buffer = save_image_to_buffer(upscaled_image)

            st.download_button(
                label="Download Stylized Image",
                data=stylized_buffer,
                file_name="stylized_image.png",
                mime="image/png"
            )

            st.download_button(
                label="Download Upscaled Image",
                data=upscaled_buffer,
                file_name="upscaled_image.png",
                mime="image/png"
            )

if __name__ == "__main__":
    main()






