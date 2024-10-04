import os
import streamlit as st
from openai import OpenAI

# Initialize OpenAI API key (ensure it's set correctly)
my_secret = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)

# Custom CSS to center the title
st.markdown("""
    <style>
        .reportview-container .main-title {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Career suggestion method
def career_suggestion(course, education_level, interests):
    system_prompt = """
    You are a career advisor with 30 years of experience. 
    You will be given a course, education level, and interests to generate 5 possible career suggestions.
    Provide a brief explanation for each suggestion.
    limit 250 words for each suggestion.
    """
    user_prompt = f"Course: {course}\nEducation Level: {education_level}\nInterests: {', '.join(interests)}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

# Improve error handling
def handle_api_error(error):
    st.error("An error occurred during API call:")
    st.write(error)  # Display specific error details

# Optional: Add an image generation feature for career-related images
# def career_image_gen(career):
#     response = client.images.generate(
#         prompt=f"An illustration representing the career of {career}",
#         n=1,
#         size="256x256"
#     )
#     return response.data[0].url

# # Add this after displaying the suggestions
# if 'suggestions' in locals():
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         if st.button("Generate a career image", use_container_width=True):
#             career_to_illustrate = st.text_input("Enter a career to illustrate:")
#             if career_to_illustrate:
#                 with st.spinner(text="Generating image..."):
#                     image_url = career_image_gen(career_to_illustrate)
#                     st.image(image_url, caption=f"Illustration for {career_to_illustrate}", use_column_width=True)
