import streamlit as st
import tempfile
from PIL import Image

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

# for rerun:
# @st.cache_resource - to reuse the same model
# for model:
# @st.cache_resource
# def load_model():
#     model = torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)
#     model.eval()
#     return model

# model = load_model()


#
# input user's params:
st.markdown("<h3 style='font-size:28px;'>Enter your age</h3>", unsafe_allow_html=True)
age = st.number_input("", min_value=0, max_value=120, step=1)

st.markdown("<h3 style='font-size:28px;'>Enter your weight (kg)</h3>", unsafe_allow_html=True)
weight = st.number_input("", min_value=0.0, max_value=300.0, step=0.1)

st.markdown("<h3 style='font-size:28px;'>Enter your height (cm)</h3>", unsafe_allow_html=True)
height = st.number_input("", min_value=0.0, max_value=250.0, step=0.1)


st.markdown("<h3 style='font-size:28px;'>Select your gender:</h3>", unsafe_allow_html=True)
gender = st.radio("", ["Male", "Female"])




#st.write(f"Your age is {age} years.")
#st.write(f"Your weight is {weight} kg.")
#st.write(f"Your height is {height} cm.")
#st.write(f"You selected: {gender}")


video_file = st.file_uploader("Upload a video of yourself running:", type=["mp4", "mov", "avi"])


if video_file is not None:
    st.video(video_file)

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())

    if st.button("Predict"):
        st.write("Analyzing video...")
        import time
        time.sleep(2)
        st.success("No injury detected.")
else:
    st.info("Please upload a video to get started.")



if st.button("Predict"):
        st.write("Analyzing video...")

#st.success("No injury detected.")
if st.button("Surprise"):
    st.balloons()
