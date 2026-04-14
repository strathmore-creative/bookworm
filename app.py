import streamlit as st
from google import genai
from google.genai import types
from pyairtable import Api
import requests
from io import BytesIO

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="Bookworm", page_icon="📖")
st.title("📖 Bookworm")
st.subheader("Character Keeper")

# These will be set up in the "Secrets" section of the web host later
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
            # Generate the Image using Gemini
            prompt = f"A professional character portrait of {name}: {description}. High detail, cinematic lighting, book illustration style."
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp", # Updated for 2026 stability
                contents=[prompt],
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
            
            # Extract Image
            for part in response.parts:
                if part.inline_data is not None:
                    image_bytes = part.as_image()
                    st.image(image_bytes, caption=f"Generated Image for {name}")
                    
                    # Save to Airtable
                    # Note: Airtable requires a public URL for attachments via API.
                    # For this simple version, we'll save the text and you can 
                    # drag the image in, OR we can use a temporary hosting service.
                    airtable.create({
                        "Name": name,
                        "Description": description
                    })
                    st.success(f"{name} has been added to your Bookworm database!")
                    
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# 4. SHOW RECENT CHARACTERS
st.divider()
st.write("### Your Library")
records = airtable.all(sort=["Created Time"])
for rec in records:
    cols = st.columns([1, 3])
    with cols[0]:
        if "Portrait" in rec["fields"]:
            st.image(rec["fields"]["Portrait"][0]["url"])
    with cols[1]:
        st.write(f"**{rec['fields'].get('Name', 'Unknown')}**")
        st.write(rec["fields"].get("Description", ""))
