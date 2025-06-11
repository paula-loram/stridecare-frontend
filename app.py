import streamlit as st
import tempfile
from PIL import Image
import cv2
import requests
import json
import pandas as pd
import time
import matplotlib.pyplot as plt

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
height = st.number_input("height", min_value=0.0, max_value=300.0, step=0.1)

st.markdown("<h3 style='font-size:28px;'>Select your gender:</h3>", unsafe_allow_html=True)
gender = st.radio("Gender", ["Male", "Female"])

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
    # st.video(video_file)

    # tfile = tempfile.NamedTemporaryFile(delete=False)
    # st.write(video_file)

    if st.button("Analyze Video"):
        # st.write("Analyzing video...")
        # url = "https://localhost:8000/generate_stickfigure"
        # # cap = cv2.VideoCapture(video_file)
        # response = requests.post(url, files={"Video": video_file.getvalue()})

        # import time
        # time.sleep(2)
        # st.success("No injury detected.")
        start_time = time.time()
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

                response = requests.post(FASTAPI_URL, files=files)
                elapsed_time = time.time() - start_time
                st.write(f"Time taken for processing: {elapsed_time:.2f} seconds")

                if response.status_code == 200:
                    st.success("Video uploaded and sent for processing successfully!")
                    result = response.json()
                    import base64
                    video_b64 = result.get("video") or result.get("video_base64")
                    angles = result.get("angles_array")  # <-- get the angles list from the response

                    if video_b64:
                        video_bytes = base64.b64decode(video_b64)
                        st.write("Processed video:")
                        st.video(video_bytes, format="video/mp4")
                    else:
                        st.error("No video found in the response.")

                    # Display angles as a dataframe if present
                    if angles:
                        df_angles = pd.DataFrame(angles)
                        # Define the columns to plot and their subplot titles
                        plot_columns = [
                            'pelvis_X', 'pelvis_Y',
                            'L_knee_X', 'L_knee_Y',
                            'R_knee_X', 'R_knee_Y',
                            'L_hip_X', 'L_hip_Y',
                            'R_hip_X', 'R_hip_Y'
                        ]
                        df_angles.columns = plot_columns
                        # st.write("Detected Angles:")
                        # st.dataframe(df_angles)



                        # Only plot if all columns are present
                        if all(col in df_angles.columns for col in plot_columns):
                            fig, axes = plt.subplots(5, 2, figsize=(12, 16))
                            axes = axes.flatten()
                            for idx, col in enumerate(plot_columns):
                                axes[idx].plot(df_angles[col])
                                axes[idx].set_title(col)
                                axes[idx].set_xlabel("Frame")
                                axes[idx].set_ylabel("Value")
                                axes[idx].set_ylim(-180, 180)  # Assuming angles are in degrees
                            plt.tight_layout()
                            st.pyplot(fig)
                        else:
                            st.warning("Not all required columns are present in the angles data.")
                        st.session_state.df_angles = df_angles  # Store df_angles in session state
                    else:
                        st.info("No angles data found in the response.")
                else:
                    st.error(f"Error uploading video: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI server. Please ensure it's running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        # import time
        # time.sleep(2)
        # st.success("No injury detected."


        FASTAPI_URL2 = "http://127.0.0.1:8000/predict/"
        with st.spinner("Analyzing video for injury detection... This might take a while."):
            try:
                angles_list = st.session_state.df_angles.values.tolist()  # Convert DataFrame to list of lists
                data = {
                    "angles": angles_list,
                    "age": age,
                    "weight": weight,
                    "height": height,
                    "gender": gender
                }
                response = requests.post(FASTAPI_URL2, json=data)
                if response.status_code == 200:
                    st.success("Injury detection completed successfully!")
                    result = response.json()
                    # Display all returned information
                    st.write("### Prediction Result")
                    st.write(f"**Prediction:** {result.get('prediction')}")
                    st.write(f"**Confidence:** {result.get('confidence')}")
                    st.write("**All Class Probabilities:**")
                    st.write(result.get("all_class_probabilities"))
                    st.write("**Details:**")
                    st.json(result.get("details"))
                    st.write("**Raw Response:**")
                    st.json(result)
                else:
                    st.error("No angles data available. Please analyze a video first.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI server. Please ensure it's running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")


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
