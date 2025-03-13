import streamlit as st
import random
import pandas as pd
from PIL import Image
import time
from io import BytesIO
import base64

# Set page config
st.set_page_config(page_title="Spanish Flash Card", page_icon="📚", layout="centered")

# Custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #B1DDC6;
    }
    .card-container {
        position: relative;
        text-align: center;
        margin: 0 auto;
        max-width: 800px;
    }
    .card-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
    }
    .title {
        font-family: Arial, sans-serif;
        font-size: 20px !important;
        font-style: italic;
        margin-bottom: 30px !important;
    }
    .word {
        font-family: Arial, sans-serif;
        font-size: 40px !important;
        font-weight: bold;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 100px;
        margin-top: 40px;
    }
    .stButton>button {
        background-color: transparent !important;
        border: none !important;
        font-size: 200px !important;
        padding: 10px 20px !important;
        margin: 0 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Image to base64 converter
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Data loading
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("data/to_learn_spanish.csv")
    except FileNotFoundError:
        data = pd.read_csv("data/spanish_words.csv")
    return data.to_dict(orient="records")


to_learn = load_data()

# Session state initialization
if "current_card" not in st.session_state:
    st.session_state.current_card = {}
if "flipped" not in st.session_state:
    st.session_state.flipped = False
if "flip_time" not in st.session_state:
    st.session_state.flip_time = time.time()


# Functions
def learn_word():
    st.session_state.current_card = random.choice(to_learn)
    st.session_state.flipped = False
    st.session_state.flip_time = time.time()


def flip_card():
    st.session_state.flipped = True


def is_known():
    if st.session_state.current_card in to_learn:
        to_learn.remove(st.session_state.current_card)
        pd.DataFrame(to_learn).to_csv("data/to_learn_spanish.csv", index=False)
    learn_word()


# UI Components
st.title("Shagun Spanish Flash Card")

# Load images
card_front = Image.open("./images/card_front.png")
card_back = Image.open("./images/card_back.png")

# Card display
if st.session_state.current_card:
    card_image = card_back if st.session_state.flipped else card_front
    title = "English" if st.session_state.flipped else "Spanish"
    word = st.session_state.current_card['English' if st.session_state.flipped else 'Spanish']
    color = "white" if st.session_state.flipped else "black"

    st.markdown(
        f"""
        <div class="card-container">
            <img src="data:image/png;base64,{image_to_base64(card_image)}" style="width:100%">
            <div class="card-text">
                <p class="title" style="color:{color}">{title}</p>
                <p class="word" style="color:{color}">{word}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Auto-flip
    if not st.session_state.flipped and time.time() - st.session_state.flip_time > 3:
        flip_card()
        st.rerun()
else:
    learn_word()
    st.rerun()

# Buttons
st.markdown('<div class="button-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    cols = st.columns(2)
    with cols[0]:
        if st.button("❌", key="wrong"):
            learn_word()
            st.rerun()
    with cols[1]:
        if st.button("✅", key="right"):
            is_known()
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Auto refresh
time.sleep(0.1)
st.rerun()
