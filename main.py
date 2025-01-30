import cv2
import pytesseract
import numpy as np
from googletrans import Translator
from moviepy.editor import VideoFileClip
import streamlit as st
import tempfile

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

def process_video(input_video, output_video, target_lang='fr'):
    clip = VideoFileClip(input_video)
    
    def process_frame(frame):
        text = extract_text_from_frame(frame)
        translated_text = translate_text(text, target_lang)
        text_boxes = [(50, 50, 200, 50)]  # Placeholder; Needs text detection
        clean_frame = remove_text_from_frame(frame, text_boxes)
        final_frame = overlay_translated_text(clean_frame, translated_text, text_boxes)
        return final_frame
    
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
