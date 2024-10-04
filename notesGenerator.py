import os
import re
import tempfile
import base64
import streamlit as st
import io
from PIL import Image
from gtts import gTTS
from openai import OpenAI
from PyPDF2 import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
import pydot

my_secret = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)

def generate_notes(content, learning_style):
    system_prompt = """
    You are an asistant that generates notes from the document/image/video/text uploaded by the user. 

    After that, you provide the user the explaination of the notes that they can use.
    Then, you provide the user with other topics and explaination of the related noted provided by the user.  
    Lastly, you provide the user with the summary of the notes.
    You are a helpful assistant that generates notes based on prompts within 1000 words limit in bullet point form according to the subtopics detected within the notes.
    You must give the notes according to the user's learning style. 

    If the user selects simplified, you must generate a simplified bullet points of the document/image/video/text uploaded by the user that is easy to do flashcards.
    If the user selects long text, you must generate a summary of the document/image/video/text with a simple explanation of the mindmap in 1000 words limit.  
    If the user selects audio, you must generate a transcription of the audio with a simple explanation of the mindmap in 1000 words limit. .

    If the user enter the image, you must generate the explaination of the image's contents.
    If the user enter the link of the video, you must generate the explaination of the video.
    """

    user_prompt = f"Learning style: {learning_style}\nContent: {content}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_youtube_transcript(video_url):
  # Extract video ID from URL
  video_id = re.findall(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url)
  if not video_id:
      return "Invalid YouTube URL"

  video_id = video_id[0]

  try:
      transcript = YouTubeTranscriptApi.get_transcript(video_id)
      full_transcript = " ".join([entry['text'] for entry in transcript])
      return full_transcript
  except Exception as e:
      return f"An error occurred while fetching the transcript: {str(e)}"

def text_to_speech(text):
  try:
      tts = gTTS(text=text, lang='en')
      with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
          tts.save(temp_audio.name)
          temp_audio_path = temp_audio.name
      return temp_audio_path
  except Exception as e:
      return f"An error occurred while generating audio: {str(e)}"

def get_audio_player_html(audio_path):
  audio_file = open(audio_path, "rb")
  audio_bytes = audio_file.read()
  audio_base64 = base64.b64encode(audio_bytes).decode()
  audio_player = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
  return audio_player
    
# # Page title
# st.title("AI Notes Generator")

# # Tabs for Document, Text, Image, Video
# tab1, tab2, tab3, tab4 = st.tabs(["Document", "Text", "Image", "Video"])

# with tab1:
#   st.write("Upload a Document")
#   uploaded_file = st.file_uploader("Drag a document here or click to browse",
#                                    type=["pdf", "txt"])

#   learning_style_doc = st.selectbox('Select your learning style:',
#                                 ['long text', 'simplified', 'audio'])

#   if st.button("Generate Notes"):
#     if uploaded_file is not None:
#       content = None
#       # Handle text files
#       if uploaded_file.type == "text/plain":
#         content = uploaded_file.getvalue().decode("utf-8")

#       # Handle PDF files
#       elif uploaded_file.type == "application/pdf":
#         try:
#           pdf_reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
#           content = ""
#           for page in pdf_reader.pages:
#             content += page.extract_text()
#         except Exception as e:
#           st.error(f"Error processing PDF: {str(e)}")

#       if content:
#         with st.spinner('Generating notes...'):
#           notes = generate_notes(content, learning_style_doc)
          
#           if learning_style_doc == 'audio':
#             audio_path = text_to_speech(notes)
#             if not audio_path.startswith("An error occurred"):
#                 st.subheader("Generated Audio:")
#                 st.markdown(get_audio_player_html(audio_path), unsafe_allow_html=True)
#                 os.unlink(audio_path)  # Delete the temporary audio file
#             else:
#                 st.error(audio_path)
              
#           st.subheader("Generated Notes:")
#           st.write(notes)
#       else:
#         st.error("Unable to extract content from the document.")
#     else:
#       st.error("Please upload a document.")

# with tab2:
#   st.write("Paste your Text")
#   text_input = st.text_area("Paste your notes here:")
#   learning_style_text = st.selectbox('Select your learning style:', ['long text', 'simplified', 'audio'], key="text")

#   if st.button("Generate Notes from Text"):
#       if text_input:
#           with st.spinner('Generating notes...'):
#               notes = generate_notes(text_input, learning_style_text)
              
#               if learning_style_text == 'audio':
#                 audio_path = text_to_speech(notes)
#                 if not audio_path.startswith("An error occurred"):
#                     st.subheader("Generated Audio:")
#                     st.markdown(get_audio_player_html(audio_path), unsafe_allow_html=True)
#                     os.unlink(audio_path)  # Delete the temporary audio file
#                 else:
#                     st.error(audio_path)
                
#               st.subheader("Generated Notes:")
#               st.write(notes)
#       else:
#           st.error("Please enter some text.")

# with tab3:
#   st.write("Upload an Image")
#   image_file = st.file_uploader("Drag an image here or click to browse",
#                                 type=["jpg", "jpeg", "png"])

#   learning_style_image = st.selectbox('Select your learning style:',
#                                       ['text', 'visual', 'audio'],
#                                       key="image")

#   if image_file is not None:
#     image = Image.open(image_file)
#     st.image(image,
#              caption=f"Uploaded Image: {image_file.name}",
#              use_column_width=True)

#   if st.button("Generate Notes from Image"):
#     with st.spinner('Analyzing image and generating notes...'):
#       notes = generate_notes(image_file, learning_style_image)

#       if learning_style_image == 'audio':
#         audio_path = text_to_speech(notes)
#         if not audio_path.startswith("An error occurred"):
#             st.subheader("Generated Audio:")
#             st.markdown(get_audio_player_html(audio_path), unsafe_allow_html=True)
#             os.unlink(audio_path)  # Delete the temporary audio file
#         else:
#             st.error(audio_path)
          
#       st.subheader("Generated Notes:")
#       st.write(notes)

# with tab4:
#   st.write("Provide a Video Link")
#   video_link = st.text_input("Enter YouTube video link:")
#   learning_style_video = st.selectbox('Select your learning style:',
#                                       ['text', 'visual', 'audio'],
#                                       key="video")

#   if st.button("Generate Notes from Video"):
#     if video_link:
#       st.write(f"Video link provided: {video_link}")
#       st.video(video_link)
#       with st.spinner('Fetching video transcript and generating notes...'):
#         transcript = get_youtube_transcript(video_link)
#         if not transcript.startswith("An error occurred"):
#           notes = generate_notes(transcript, learning_style_video)

#           if learning_style_video == 'audio':
#             audio_path = text_to_speech(transcript)
#             if not audio_path.startswith("An error occurred"):
#                 st.subheader("Generated Audio:")
#                 st.markdown(get_audio_player_html(audio_path), unsafe_allow_html=True)
#                 os.unlink(audio_path)  # Delete the temporary audio file
#             else:
#                 st.error(audio_path)

#           st.subheader("Generated Notes:")
#           st.write(notes)

#         else:
#           st.error(transcript)
#     else:
#       st.error("Please enter a valid YouTube video link.")




