import os
import time
import streamlit as st
from openai import OpenAI
from PIL import Image
import PyPDF2
import io
import base64
from youtube_transcript_api import YouTubeTranscriptApi
import re
from collections import defaultdict
from gtts import gTTS
import tempfile
import notesGenerator, career, insight
import pydot
from streamlit_option_menu import option_menu

# Set page configurations as the first Streamlit command
st.set_page_config(
    page_title="MasterMind AI",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to inject local CSS
def local_css(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply custom CSS
local_css("style.css")

# Initialize OpenAI API key
my_secret = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)

# Display a banner image
st.image("banner.jpg", use_column_width=True)

def main():
    # Initialize session state variables
    if 'current_step' not in st.session_state:
        st.session_state[
            'current_step'] = 0  # 0: Home, 1: Upload, 2: Summary, etc.
    if 'notes' not in st.session_state:
        st.session_state['notes'] = None
    if 'insight' not in st.session_state:
        st.session_state['insight'] = None
    if 'possible_career' not in st.session_state:
        st.session_state['possible_career'] = None
    #if 'history' not in st.session_state:
    #    st.session_state['history'] = None

    
    steps = [
        "Home", "AI Notes Generator", "Insight", "Possible Career",
    ]

    # Sidebar for navigation using option_menu
    with st.sidebar:
        selected_step = option_menu(
            menu_icon="cast",
            default_index=st.session_state['current_step'],
            orientation="vertical",
            options=steps,
            menu_title=None,
            styles={
                "container": {
                    "padding": "5!important",
                    "background-color": "#000000"
                },
                "icon": {
                    "color": "#e56717",
                    "font-size": "25px"
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "2px",
                    "--hover-color": "#000000",
                },
                "nav-link-selected": {
                    "background-color": "#e56717",
                    "color": "white"
                },
            })
        
        st.session_state['current_step'] = steps.index(selected_step)

    # App logic based on current step
    # Home page layout
    if st.session_state['current_step'] == 0:
        st.title("MasterMind AI: Your Smart Learning Assistant")
        st.divider()
        # Create two columns: one for text and one for the start button
        col1, col2 = st.columns([2.5, 1.5])

        with col1:
            st.markdown("""
                ### 
                **Improve your learning process with MasterMind AI.**  
                With **MasterMind AI**, you can:

                | #  | Features                       | Description                                            |
                |----|--------------------------------|--------------------------------------------------------|
                | 1  | **Notes Generator**            | Quickly analyze your research documents.               |
                | 2  | **Insight**                    | Capture key insights from your documents.              |
                | 3  | **Career Path**                | Find gaps in research to refine your focus.            |


                _Turn your current documents into notes in multiple forms with expert AI assistance. Click the button below to get started!_
                """)
        with col2:
            # Space above the button to center it vertically
            st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
            if st.button("Get Started", key="start_button"):
                st.session_state['current_step'] = 1
                st.rerun()

    elif st.session_state['current_step'] == 1:
        # Page title
        st.header("1. Notes Generator")
        st.divider()
        # Tabs for Document, Text, Image, Video
        tab1, tab2, tab3, tab4 = st.tabs(["Document", "Text", "Image", "Video"])

        with tab1:
            st.write("Upload a Document")
            uploaded_file = st.file_uploader("Drag a document here or click to browse", type=["pdf", "txt"])

            learning_style_doc = st.selectbox('Select your learning style:', ['long text', 'simplified', 'audio'])

            if st.button("Generate Notes"):
                if uploaded_file is not None:
                    content = None
                    # Handle text files
                    if uploaded_file.type == "text/plain":
                        content = uploaded_file.getvalue().decode("utf-8")

                    # Handle PDF files
                    elif uploaded_file.type == "application/pdf":
                        try:
                            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
                            content = ""
                            for page in pdf_reader.pages:
                                content += page.extract_text()
                        except Exception as e:
                            st.error(f"Error processing PDF: {str(e)}")

                    if content:
                        with st.spinner('Generating notes...'):
                            notes = notesGenerator.generate_notes(content, learning_style_doc)

                            

                            if learning_style_doc == 'audio':
                                audio_path = notesGenerator.text_to_speech(notes)

                                if not audio_path.startswith("An error occurred"):
                                    st.subheader("Generated Audio:")
                                    st.markdown(notesGenerator.get_audio_player_html(audio_path), unsafe_allow_html=True)
                                    os.unlink(audio_path)  # Delete the temporary audio file
                                else:
                                    st.error(audio_path)


                            st.subheader("Generated Notes:")
                            st.write(notes)
                    else:
                        st.error("Unable to extract content from the document.")
                else:
                    st.error("Please upload a document.")

        with tab2:
          st.write("Paste your Text")
          text_input = st.text_area("Paste your notes here:")
          learning_style_text = st.selectbox('Select your learning style:', ['long text', 'simplified', 'audio'], key="text")

          if st.button("Generate Notes from Text"):
              if text_input:
                  with st.spinner('Generating notes...'):
                      notes = notesGenerator.generate_notes(text_input, learning_style_text)
                      st.session_state['notes'] = notes 

                      if learning_style_text == 'audio':
                        audio_path = notesGenerator.text_to_speech(notes)
                          
                        if not audio_path.startswith("An error occurred"):
                            st.subheader("Generated Audio:")
                            st.markdown(notesGenerator.get_audio_player_html(audio_path), unsafe_allow_html=True)
                            os.unlink(audio_path)  # Delete the temporary audio file
                        else:
                            st.error(audio_path)

                      st.subheader("Generated Notes:")
                      st.write(notes)
              else:
                  st.error("Please enter some text.")

        with tab3:
          st.write("Upload an Image")
          image_file = st.file_uploader("Drag an image here or click to browse",
                                        type=["jpg", "jpeg", "png"])

          learning_style_image = st.selectbox('Select your learning style:',
                                              ['long text', 'simplified', 'audio'],
                                              key="image")

          if image_file is not None:
            image = Image.open(image_file)
            st.image(image,
                     caption=f"Uploaded Image: {image_file.name}",
                     use_column_width=True)

          if st.button("Generate Notes from Image"):
            with st.spinner('Analyzing image and generating notes...'):
              notes = notesGenerator.generate_notes(image_file, learning_style_image)
              st.session_state['notes'] = notes

              if learning_style_image == 'audio':
                audio_path = notesGenerator.text_to_speech(notes)
                if not audio_path.startswith("An error occurred"):
                    st.subheader("Generated Audio:")
                    st.markdown(notesGenerator.get_audio_player_html(audio_path), unsafe_allow_html=True)
                    os.unlink(audio_path)  # Delete the temporary audio file
                else:
                    st.error(audio_path)

              st.subheader("Generated Notes:")
              st.write(notes)

        with tab4:
          st.write("Provide a Video Link")
          video_link = st.text_input("Enter YouTube video link:")
          learning_style_video = st.selectbox('Select your learning style:',
                                              ['long text', 'simplified', 'audio'],
                                              key="video")

          if st.button("Generate Notes from Video"):
            if video_link:
              st.write(f"Video link provided: {video_link}")
              st.video(video_link)
              with st.spinner('Fetching video transcript and generating notes...'):
                transcript = notesGenerator.get_youtube_transcript(video_link)
                if not transcript.startswith("An error occurred"):
                  notes = notesGenerator.generate_notes(transcript, learning_style_video)
                  st.session_state['notes'] = notes

                  if learning_style_video == 'audio':
                    audio_path = notesGenerator.text_to_speech(transcript)
                    if not audio_path.startswith("An error occurred"):
                        st.subheader("Generated Audio:")
                        st.markdown(notesGenerator.get_audio_player_html(audio_path), unsafe_allow_html=True)
                        os.unlink(audio_path)  # Delete the temporary audio file
                    else:
                        st.error(audio_path)

                  st.subheader("Generated Notes:")
                  st.write(notes)

                else:
                  st.error(transcript)
            else:
              st.error("Please enter a valid YouTube video link.")
                        
    # Insight
    elif st.session_state['current_step'] == 2:
        
        st.header("2. Insight")
        st.divider()
        st.markdown("Welcome to the Insight Generator! Your one-stop shop for mind-blowing insights.")

        if 'notes' in st.session_state:
            if st.button(" Generate Insights"):
                # Fun and entertaining spinner
                with st.spinner(insight.playful_message()):
                    insights = insight.generate_insights(st.session_state['notes']) #st.session_state['notes']
                    time.sleep(2)  # Add a delay to simulate process time

                # Display insights with emojis for added fun
                st.subheader(" Your Genius Insights:")
                insights_box = st.text_area("", value=insights, height=300, key="insights_box")

                if st.button(" Copy"):
                    st.write("copied")
                    st.experimental_set_query_params(insights=insights)
                    st.balloons()  # Fun balloon animation
            else:
                st.write("Feeling curious? Click the button and let's dive into some insights! ")
        else:
            st.warning("Please generate notes first on the Notes Generator page. 💬")
        
    # Career path
    elif st.session_state['current_step'] == 3:
        st.header("3. Career Path")
        st.divider()

        # Center the course input
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            course = st.text_input("Enter your course:")

        # Education level and interests selection
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            education_level = st.selectbox(
                "Select your education level:",
                ("High School", "Bachelor's", "Master's", "PhD")
            )
        with col2:
            with st.expander("Select your interests (optional)"):  # Use expander for optional input
                interests = st.multiselect(
                    "Select your interests:",
                    ["Technology", "Science", "Arts", "Business", "Healthcare", "Education"]
                )

        # Center the generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_button = st.button("Generate Career Suggestions", use_container_width=True)

            # Add custom CSS to style the button
            st.markdown(
                """
                <style>
                    .stButton button {
                        background-color: black;
                        color: white;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )

        if generate_button:
            if course:
                try:
                    with st.spinner(text="Generating suggestions..."):
                        suggestions = career.career_suggestion(course, education_level, interests)
                        st.session_state['possible_career'] = suggestions
                        st.success("Career suggestions generated!")
                        st.write(suggestions)
                except Exception as e:  # Catch potential errors
                    career.handle_api_error(e)
            else:
                st.warning("Please enter a course before generating suggestions.")
                

        

if __name__ == "__main__":
    main()
