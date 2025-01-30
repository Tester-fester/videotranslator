import cv2
import pytesseract
import numpy as np
from googletrans import Translator
from moviepy.editor import VideoFileClip
import streamlit as st
import tempfile
import os

# Initialize translator
translator = Translator()

def extract_text_from_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='eng')
    return text.strip()

def translate_text(text, target_lang='fr'):
    translated = translator.translate(text, dest=target_lang)
    return translated.text

def remove_text_from_frame(frame, text_boxes):
    mask = np.zeros_like(frame)
    for (x, y, w, h) in text_boxes:
        mask[y:y+h, x:x+w] = 255
    
    inpainted_frame = cv2.inpaint(frame, cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY), 3, cv2.INPAINT_TELEA)
    return inpainted_frame

def overlay_translated_text(frame, translated_text, text_boxes):
    for (box, text) in zip(text_boxes, translated_text.split('\n')):
        x, y, w, h = box
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    return frame

def detect_text_boxes(frame):
    # Use pytesseract to get bounding boxes for text regions
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    d = pytesseract.image_to_boxes(gray)
    text_boxes = []
    h, w = frame.shape[:2]
    for b in d.splitlines():
        b = b.split()
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        text_boxes.append((x, y, w - x, h - y))  # (x, y, width, height)
    return text_boxes

def process_video(input_video, output_video, target_lang='fr'):
    clip = VideoFileClip(input_video)
    
    def process_frame(frame):
        text = extract_text_from_frame(frame)
        translated_text = translate_text(text, target_lang)
        
        text_boxes = detect_text_boxes(frame)  # Get dynamic text boxes
        clean_frame = remove_text_from_frame(frame, text_boxes)
        final_frame = overlay_translated_text(clean_frame, translated_text, text_boxes)
        return final_frame
    
    # Add a progress bar for Streamlit to track processing progress
    new_clip = clip.fl_image(process_frame)
    new_clip.write_videofile(output_video, codec='libx264', fps=clip.fps)

# Streamlit UI
st.title("Video Text Translator")
st.write("Upload a video, choose a target language, and get the translated version with replaced on-screen text.")

uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
target_lang = st.text_input("Target Language Code (e.g., 'fr' for French)", "fr")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_file.read())
        temp_video_path = temp_video.name

    output_video_path = "output.mp4"
    process_video(temp_video_path, output_video_path, target_lang)

    st.video(output_video_path)

    # Clean up temporary files
    os.remove(temp_video_path)
