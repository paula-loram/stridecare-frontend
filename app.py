import streamlit as st
from PIL import Image
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
import openai
import base64

# --- Model's output labels and their order --- --------> DOES ORDER MATTER?
MODEL_OUTPUT_LABELS = [
    "No injury",
    "Knee",
    "Foot/Ankle",
    "Hip/Pelvis",
    "Thigh",
    "Lower Leg"
]


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
        FASTAPI_URL = "https://stridecare-25101518845.europe-west2.run.app/get_stick_fig_video/"

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
                        video_base64 = base64.b64encode(video_bytes).decode()
                        video_html = f"""
                            <video width="400" height="225" controls>
                                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        """
                        st.markdown(video_html, unsafe_allow_html=True)
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


        FASTAPI_URL2 = "https://stridecare-25101518845.europe-west2.run.app/predict/"
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

                # Get result
                result = response.json()
                prediction = result["prediction"]
                confidence = result["confidence"]
                prob_dict = result["all_class_probabilities"]

                # Sort and map probabilities
                sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
                top_3 = [(MODEL_OUTPUT_LABELS[int(i)], p) for i, p in sorted_probs[:3]]

                # Display main prediction
                if prediction != "No injury":
                    st.markdown(
                        f"## 😟 Uh-oh! A **risk of injury** was detected.\n"
                        f"**Likely issue:** *{prediction}*  \n"
                        f"**Confidence:** {confidence*100:.1f}%"
                    )
                else:
                    st.markdown(
                        f"## 🎉 Great news — You're looking strong!\n"
                        f"**No injury detected** with {confidence*100:.1f}% confidence. Keep running happy!"
                    )

                # Friendly top 3 breakdown
                st.markdown("### 🔍 Here's what StrideCare saw as most likely:")
                for i, (label, prob) in enumerate(top_3, 1):
                    st.markdown(f"{i}. **{label}** — {prob*100:.1f}%")

                # Save for GPT prompt
                predicted_injury = top_3[0][0]
                alt_predictions = ", ".join([f"{label} ({prob*100:.1f}%)" for label, prob in top_3[1:]])

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI server. Please ensure it's running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")


# GPT-based report generation

# Injury type dict #these are the same ''MODEL_OUTPUT_LABELS''
# Providing an informed description with no jargon
    injury_types = {
    "No injury": "Runner has good form, and is not prone to injury",
    "Foot/Ankle": "Runner shows signs of stress or dysfunction in the foot or ankle, possibly indicating an issue with their arch-heel, an achilles issue, or ankle instability.",
    "Hip/Pelvis": "Runner exhibits movement patterns or weaknesses around the hip/pelvis, which could be caused by their glutes, hip impingement, or poor pelvic stability.",
    "Thigh": "A biomechanical indicator of strain or overuse in the thigh muscles, commonly involving the hamstrings or quadriceps, which may lead to strains or muscle imbalances.",
    "Lower Leg": "Runner may be at risk for conditions like shin splints or calf strain, often due to overuse, poor shock absorption, or inadequate lower-leg strength."
}


        # OpenAI key
    openai.api_key = st.secrets["OPEN_AI_KEY_POlINA"]


    # GPT-based report generation
    def injury_report(predicted_injury, age, gender, height, weight, max_tokens=250): # Tokens determine the number of words in the summary
        system_prompt = (
            "You are a friendly and helpful Sports Therapist. "
            "You are to explain the runner's injury assessment results using concise and simple language that's easy for the runner to understand. "
            "You avoid medical jargon, speak with warmth, and gently guide the runner on what to do next to address their injury, which involves a Recovery Strategy, Stretching Plan, and Strengthening Plan. "
            "Limit to about 200 words. "
        )

        prompt = f"""
        Our, StrideCare, running-injury assessment AI model predicted: {injury_types.get(predicted_injury, 'Unkown Injury')}

        The runner's details:
        - Age: {age}
        - Gender: {gender}
        - Height: {height}
        - Weight: {weight}

        In a friendly, concise, and detailed manner without jargon, please provide a complete-plan to help the runner address their injury.
        We want to provide a full-complete plan which addresses their {predicted_injury} injury:
            Recovery strategies (e.g. resting, walking, swimming, etc.) which is relevant to their {predicted_injury} injury,
            A specific and tailored Stretching plan addressing their {predicted_injury} injury, we want the names of stretches, how many repetitions/seconds and number of sets,
            and we want a specific and tailored Strengthening plan for the {predicted_injury} injury, including weighted and/or free-weight exercises with ideally as little equipment as possible, please provide the names of these exercises along with number of repetitions and sets.
        Remember, the plan is to ultimately help them run injury free with this tailored plan.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()


    ## Calling upon injury_report using streamlit
    if st.button("Get Injury Report"):
        # Calls upon injury_report with the inputs from the streamlit website
        report = injury_report(predicted_injury, age, gender, height, weight)
        st.subheader("Injury Recovery Plan")
        st.write(report)


            #     response = requests.post(FASTAPI_URL2, json=data)
            #     if response.status_code == 200:
            #         st.success("Injury detection completed successfully!")
            #         result = response.json()
            #         # Display all returned information
            #         st.write("### Prediction Result")
            #         st.write(f"**Prediction:** {result.get('prediction')}")
            #         st.write(f"**Confidence:** {result.get('confidence')}")
            #         st.write("**All Class Probabilities:**")
            #         st.write(result.get("all_class_probabilities"))
            #         st.write("**Details:**")
            #         st.json(result.get("details"))
            #         st.write("**Raw Response:**")
            #         st.json(result)
            #     else:
            #         st.error("No angles data available. Please analyze a video first.")
            # except requests.exceptions.ConnectionError:
            #     st.error("Could not connect to the FastAPI server. Please ensure it's running.")
            # except Exception as e:
            #     st.error(f"An unexpected error occurred: {e}")
