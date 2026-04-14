import streamlit as st
from google import genai
from google.genai import types
from pyairtable import Api

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="Bookworm", page_icon="📖")
st.title("📖 Bookworm")
st.subheader("Character Keeper")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
TABLE_NAME = "Characters"

# Initialize Clients
client = genai.Client(api_key=GEMINI_API_KEY)
airtable = Api(AIRTABLE_PAT).table(AIRTABLE_BASE_ID, TABLE_NAME)

# 2. THE INTERFACE
with st.form("character_form"):
    name = st.text_input("Character Name")
    description = st.text_area("Description (Physical traits, clothing, vibe...)")
    submit = st.form_submit_button("Bring to Life")

# 3. THE LOGIC
if submit and name and description:
    with st.spinner(f"Visualizing {name}..."):
        try:
            # Using the stable 2026 image generation method
            prompt = f"A professional character portrait of {name}: {description}. High detail, cinematic lighting, book illustration style."
            
            # Alternative call for maximum compatibility
            response = client.images.generate(
                model="imagen-3.0-generate-001",
                prompt=prompt
            )
            
            # Extract and display the image
            image_bytes = response.generated_images[0].image_bytes
            st.image(image_bytes, caption=f"Generated Image for {name}")
            
            # Save to Airtable
            airtable.create({
                "Name": name,
                "Description": description
            })
            st.success(f"{name} has been added to your Bookworm database!")

# 4. SHOW RECENT CHARACTERS
st.divider()
st.write("### Your Library")
try:
    records = airtable.all()
    for rec in records:
        cols = st.columns([1, 3])
        with cols[0]:
            if "Portrait" in rec["fields"]:
                st.image(rec["fields"]["Portrait"][0]["url"])
        with cols[1]:
            st.write(f"**{rec['fields'].get('Name', 'Unknown')}**")
            st.write(rec["fields"].get("Description", ""))
except Exception:
    st.info("Your library is empty. Add your first character above!")
