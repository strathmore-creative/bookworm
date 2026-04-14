import streamlit as st
import requests
from pyairtable import Api

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="Bookworm", page_icon="📖", layout="wide")
st.title("📖 Bookworm Character Curator")

# Load Secrets
try:
    PIXABAY_API_KEY = st.secrets["PIXABAY_API_KEY"]
    AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
    AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
    TABLE_NAME = "Characters"
    
    # Initialize Airtable
    airtable = Api(AIRTABLE_PAT).table(AIRTABLE_BASE_ID, TABLE_NAME)
except Exception as e:
    st.error("Missing Secrets! Check your Streamlit Cloud settings.")
    st.stop()

# 2. THE SIDEBAR (Input Section)
with st.sidebar:
    st.header("1. Character Details")
    name = st.text_input("Character Name", placeholder="e.g., Rupert")
    description = st.text_area("Physical Traits", placeholder="e.g., man in his 30s, realistic portrait, cinematic lighting")
    search_btn = st.button("Find Portraits")

# 3. THE MAIN GALLERY (Selection Section)
if search_btn and description:
    # Build the Pixabay Search URL
    # We add 'photo' and 'en' to ensure we get realistic English-tagged results
    pixabay_url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={description}&image_type=photo&per_page=4"
    
    with st.spinner("Searching Pixabay..."):
        response = requests.get(pixabay_url).json()
        
    if response.get('hits'):
        st.write(f"### Select a Portrait for **{name}**")
        cols = st.columns(4) # Create a 4-column layout
        
        for i, hit in enumerate(response['hits']):
            with cols[i]:
                img_url = hit['webformatURL']
                st.image(img_url, use_container_width=True)
                
                # Each button has a unique 'key' so Streamlit doesn't get confused
                if st.button(f"Save Option {i+1}", key=f"save_{i}"):
                    try:
                        # We send Name, Description, and the URL to Airtable
                        airtable.create({
                            "Name": name,
                            "Description": description,
                            "Portrait": [{"url": img_url}]
                        })
                        st.balloons()
                        st.success(f"Successfully saved {name} to Airtable!")
                    except Exception as err:
                        st.error(f"Airtable Error: {err}")
    else:
        st.warning("No photos found. Try broader keywords like 'man' or 'woman' or 'face'.")

# 4. THE LIBRARY (View Section)
st.divider()
st.write("### Your Library")
try:
    records = airtable.all()
    if not records:
        st.info("Your library is empty. Start by searching in the sidebar!")
    else:
        for rec in records:
            fields = rec['fields']
            c1, c2 = st.columns([1, 4])
            with c1:
                if "Portrait" in fields:
                    st.image(fields["Portrait"][0]["url"], width=150)
            with c2:
                st.write(f"#### {fields.get('Name', 'Unnamed')}")
                st.write(fields.get('Description', 'No description provided.'))
except Exception:
    pass
