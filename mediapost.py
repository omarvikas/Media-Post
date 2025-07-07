# app.py

import streamlit as st
from openai import OpenAI
from PIL import Image

st.set_page_config(page_title="📢 Event Post Generator", layout="centered")
st.title("📢 Event Post Generator for LinkedIn, WhatsApp, and Newspaper")

# --- API Key ---
api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
if not api_key:
    st.warning("Please enter your API key to continue.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- Event Details Form ---
with st.form("event_form"):
    event_name = st.text_input("🎯 Event Name (e.g., 'Children’s Day Celebration with Mindspark')", max_chars=100)
    event_date = st.date_input("📅 Event Date")
    location = st.text_input("📍 Location (e.g., Telangana & Andhra Pradesh)")
    focus_area = st.selectbox("👥 Who is the event about?", ["Students", "Teachers", "Schools"])
    partner_names = st.text_area("🤝 Partner/Supporter Names (comma-separated)")
    tags = st.text_area("🏷️ People or Organizations to Tag (LinkedIn only, comma-separated)", help="Optional")
    highlights = st.text_area("🌟 Highlights (enter as many specific details as possible)", height=150)
    uploaded_images = st.file_uploader("🖼️ Upload Image(s) (optional, used to inspire the tone)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    output_types = st.multiselect("📤 Which outputs do you want to generate?", ["LinkedIn", "WhatsApp", "Newspaper"])

    whatsapp_audience = None
    if "WhatsApp" in output_types:
        whatsapp_audience = st.selectbox("👥 WhatsApp Audience", ["Students", "Teachers", "Principals", "Field Team", "Leadership Team", "Peers"])

    submitted = st.form_submit_button("Generate Posts")

# --- Prompt Construction ---
def build_prompt(post_type):
    image_note = f"{len(uploaded_images)} image(s) showing the event" if uploaded_images else "No images uploaded"
    base_prompt = f"""
Event Name: {event_name}
Date: {event_date.strftime('%d %B %Y')}
Location: {location}
Focus Area: {focus_area}
Highlights: {highlights}
Partners: {partner_names}
Tags: {tags}
Images: {image_note}
"""

    if post_type == "LinkedIn":
        return base_prompt + f"""
You are a communications expert writing a warm, professional LinkedIn post.
The post just happened or is very recent.
Use a catchy heading and keep the tone narrative, celebrating student or teacher achievements.
Include hashtags and tag people listed.
Length: under 200 words.
"""
    elif post_type == "WhatsApp":
        return base_prompt + f"""
You are writing a slightly informal and emotional WhatsApp message.
Audience: {whatsapp_audience}
Write one catchy heading followed by 3–5 lines of message.
Tone: just happened, inspiring and conversational.
Keep it under ~400 characters.
"""
    elif post_type == "Newspaper":
        return base_prompt + f"""
You are a newspaper reporter summarizing an educational event.
Write in formal, third-person style. Include:
- A title and subtitle
- Date and location in the opening
- Highlights of the event
Tone: recent and factual, but inspiring.
Length: 250–350 words.
"""
    return ""

# --- Output Section ---
if submitted:
    st.subheader("📄 Generated Outputs")

    for post_type in output_types:
        with st.spinner(f"Generating {post_type} post..."):
            try:
                prompt = build_prompt(post_type)
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                post_text = response.choices[0].message.content
                st.markdown(f"### 📝 {post_type} Post")
                st.text_area(label="", value=post_text, height=250)
            except Exception as e:
                st.error(f"Error generating {post_type} post: {e}")
