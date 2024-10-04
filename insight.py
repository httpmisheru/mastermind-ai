import os
from openai import OpenAI
from openai.resources import chat
import streamlit as st
import time

# Set OpenAI API key
my_secret = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)

def generate_insights(notes):
        prompt = f"Generate fun and witty insights from the following notes:\n\n{notes}\n\nCreative Insights:"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fun and creative assistant that generates witty insights from notes."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

def playful_message():
        # Add playful responses
        messages = [
            "Hold tight! Your brain is about to be blown ",
            "Getting those insights, just a sec... ",
            "Working on it... ",
            "Magic is happening...",
        ]
        return messages[int(time.time()) % len(messages)]  # Rotate messages based on time

