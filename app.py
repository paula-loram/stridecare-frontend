import streamlit as st
import tempfile
from PIL import Image
import cv2
import requests

# ! use only external url !



# backgroung color

st.markdown(
    """
    <style>
    .stApp {
        background-color: #83bbf7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load the image from file
img = Image.open("cover.png")

# Resize the image (width=px, height=2px)
img = img.resize((1000, 500))

# Display the resized image
st.image(img)

st.title("StrideCare")
st.subheader("Analyze your stride, strengthen your run, prevent injuries.")

# input user's params:
st.markdown("<h3 style='font-size:28px;'>Enter your age</h3>", unsafe_allow_html=True)
age = st.number_input("Age", min_value=0, max_value=120, step=1)

st.markdown("<h3 style='font-size:28px;'>Enter your weight (kg)</h3>", unsafe_allow_html=True)
weight = st.number_input("Weight", min_value=0.0, max_value=300.0, step=0.1)

st.markdown("<h3 style='font-size:28px;'>Enter your height (cm)</h3>", unsafe_allow_html=True)
height = st.number_input("Height", min_value=0.0, max_value=250.0, step=0.1)


st.markdown("<h3 style='font-size:28px;'>Select your gender:</h3>", unsafe_allow_html=True)
gender = st.radio("Gender", ["Male", "Female"])


video_file = st.file_uploader("Upload a video of yourself running:", type=["mp4", "mov", "avi"])


if video_file is not None:
    # st.video(video_file)

    # tfile = tempfile.NamedTemporaryFile(delete=False)
    # st.write(video_file)

    if st.button("Predict"):
        st.write("Analyzing video...")
        FASTAPI_URL = "http://127.0.0.1:8000/get_stick_fig_video/"

        with st.spinner("Uploading and processing video... This might take a while."):
            try:
                files = {
                    "video": (
                        video_file.name,
                        video_file.getvalue(),
                        video_file.type
                    )
                }
                # Send user parameters as a JSON string in a form field
                import json
                data = {
                    "params": json.dumps({
                        "age": age,
                        "weight": weight,
                        "height": height,
                        "gender": gender
                    })
                }
                response = requests.post(FASTAPI_URL, files=files, data=data, stream=True)

                if response.status_code == 200:
                    st.success("Video uploaded and sent for processing successfully!")
                    video_bytes = response.content
                    st.write("Processed video:")
                    st.video(video_bytes, format="video/mp4")
                else:
                    st.error(f"Error uploading video: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI server. Please ensure it's running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        # import time
        # time.sleep(2)
        # st.success("No injury detected.")

else:
    st.info("Please upload a video to get started.")



#st.success("No injury detected.")
if st.button("Surprise"):
    st.balloons()
