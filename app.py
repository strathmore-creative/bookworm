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
            # Use the dedicated Image Generation tool
            prompt = f"A professional character portrait of {name}: {description}. High detail, cinematic lighting, book illustration style."
            
            # This call uses the specialized Imagen 3 model
            response = client.models.generate_image(
                model="imagen-3.0-generate-001",
                prompt=prompt,
                config=types.GenerateImageConfig(
                    number_of_images=1
                )
            )
            
            # Display the generated image
            image_bytes = response.generated_images[0].image_bytes
            st.image(image_bytes, caption=f"Generated Image for {name}")
            
            # Save to Airtable
            airtable.create({
                "Name": name,
                "Description": description
            })
            st.success(f"{name} has been added to your Bookworm database!")
            
        except Exception as e:
            # If the tool is missing, try the alternative "images" route
            try:
                response = client.images.generate(model="imagen-3.0-generate-001", prompt=prompt)
                st.image(response.generated_images[0].image_bytes, caption=f"Generated Image for {name}")
                airtable.create({"Name": name, "Description": description})
                st.success(f"{name} has been added to your database!")
            except Exception as e2:
                st.error(f"Image generation is currently unavailable: {e2}")

# 4. SHOW RECENT CHARACTERS
st.divider()
st.write("### Your Library")
try:
    records = airtable.all()
    if not records:
        st.info("Your library is empty. Add your first character above!")
    else:
        for rec in records:
            cols = st.columns([1, 3])
            with cols[0]:
                # Check if there is an image URL in Airtable (if you've added one manually)
                if "Portrait" in rec["fields"]:
                    st.image(rec["fields"]["Portrait"][0]["url"])
                else:
                    st.write("🖼️") # Placeholder if no image yet
            with cols[1]:
                st.write(f"**{rec['fields'].get('Name', 'Unknown')}**")
                st.write(rec["fields"].get("Description", ""))
except Exception as e:
    st.warning("Could not load library from Airtable. Check your Table Name.")
