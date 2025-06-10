import streamlit as st
import tempfile

# ! use only external url !

st.title("Injury Detection from Video")

# for rerun:
# @st.cache_resource - to reuse the same model
# for model:
# @st.cache_resource
# def load_model():
#     model = torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)
#     model.eval()
#     return model

# model = load_model()



# input user's params:

age = st.number_input("Enter your age", min_value=0, max_value=120, step=1)

weight = st.number_input("Enter your weight (kg)", min_value=0.0, max_value=300.0, step=0.1)

height = st.number_input("Enter your height (cm)", min_value=0.0, max_value=250.0, step=0.1)

st.write(f"Your age is {age} years.")
st.write(f"Your weight is {weight} kg.")
st.write(f"Your height is {height} cm.")
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
