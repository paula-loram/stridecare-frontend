import streamlit as st
import tempfile
import requests
import time
import json

# Page setup & styles
st.set_page_config(page_title="StrideCare", page_icon="🏃‍♂️")
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

st.title("StrideCare")
st.subheader("Analyze your stride, strengthen your run, prevent injuries.")

# User inputs
age = st.number_input("Enter your age", min_value=0, max_value=120, step=1)
height = st.number_input("Enter your height (cm)", min_value=0.0, max_value=250.0, step=0.1)
weight = st.number_input("Enter your weight (kg)", min_value=0.0, max_value=300.0, step=0.1)
gender = st.radio("Select your gender", ["Male", "Female"])

metadata = {
    "age": age,
    "height": height,
    "weight": weight,
    "gender": gender
}

video_file = st.file_uploader("Upload a video of yourself running:", type=["mp4", "mov", "avi"])

if video_file is not None:
    st.video(video_file)

    if st.button("Analyze and Predict"):
        with st.spinner("Uploading video and metadata..."):
            # Save uploaded video to temp file
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(video_file.read())
            tfile.flush()

            url = "http://localhost:8000/predict"  # Replace with your actual API URL

            # Prepare multipart/form-data for video and form data for metadata JSON
            files = {"video": open(tfile.name, "rb")}
            data = {"metadata": json.dumps(metadata)}

            try:
                response = requests.post(url, files=files, data=data)
                response.raise_for_status()
                res_json = response.json()
                prediction_id = res_json["prediction_id"]
                stick_figure_url = res_json["stick_figure_url"]
            except Exception as e:
                st.error(f"Error during prediction request: {e}")
                st.stop()

        # Show stick figure video immediately
        st.video(stick_figure_url)

        # Placeholder for prediction result
        result_placeholder = st.empty()

        # Poll prediction status endpoint
        status_url = f"http://localhost:8000/prediction_status/{prediction_id}"

        for _ in range(20):  # poll up to 20 times (1 min)
            try:
                status_resp = requests.get(status_url)
                status_resp.raise_for_status()
                status_data = status_resp.json()
            except Exception as e:
                result_placeholder.error(f"Error checking prediction status: {e}")
                break

            if status_data.get("ready"):
                result_placeholder.success(f"Prediction result: {status_data.get('result')}")
                break
            else:
                result_placeholder.info("Prediction is processing, please wait...")
                time.sleep(3)
        else:
            result_placeholder.warning("Prediction timeout or failed.")

else:
    st.info("Please upload a video to get started.")
