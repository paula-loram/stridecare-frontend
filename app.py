import streamlit as st
import tempfile
from PIL import Image
import cv2
import requests
import json

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
age = st.number_input("", min_value=0, max_value=120, step=1)

st.markdown("<h3 style='font-size:28px;'>Enter your height (cm)</h3>", unsafe_allow_html=True)
height = st.number_input("", min_value=0.0, max_value=250.0, step=0.1)

st.markdown("<h3 style='font-size:28px;'>Enter your weight (kg)</h3>", unsafe_allow_html=True)
weight = st.number_input("", min_value=0.0, max_value=300.0, step=0.1)

st.markdown("<h3 style='font-size:28px;'>Select your gender:</h3>", unsafe_allow_html=True)
gender = st.radio("", ["Male", "Female"])

#creating dictionary out of user params
metadata = {
    "age": age,
    "height": height,
    "weight": weight,
    "gender": gender
}

#sending to fastAPI
metadata_dir = {'metadata': metadata}

#getting video uploaded by user
video_file = st.file_uploader("Upload a video of yourself running:", type=["mp4", "mov", "avi"])



if video_file is not None:
    st.video(video_file)

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())

    if st.button("Predict"):
        st.write("Analyzing video...")
        url = "https://localhost:8000/generate_stickfigure"
        # cap = cv2.VideoCapture(video_file)
        response = requests.post(url, files={"Video": video_file.getvalue()})
        
        import time
        time.sleep(2)
        st.success("No injury detected.")
else:
    st.info("Please upload a video to get started.")


if st.button("Predicts"):

        st.write("Analyzing video...")

#st.success("No injury detected.")
if st.button("Surprise"):
    st.balloons()

# background_tasks : call on another endpoint
#send metadata w video (op1)

#option 2: sequentially
#but starting with predict endpoint (big), then we can do get stickfigure
# coord + video embedded, returning new video in api
#easier: get videos in: coordinates as result of endpoint
#then second endpoint w metadata + coordinates --> model prediction to get injury classes
#can also display angle plot
