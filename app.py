import streamlit as st
import requests
from pyairtable import Api

# 1. SETUP
st.set_page_config(page_title="Bookworm", page_icon="📖", layout="wide")

# Load Secrets
PIXABAY_API_KEY = st.secrets["PIXABAY_API_KEY"]
AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
TABLE_NAME = "Characters"

airtable = Api(AIRTABLE_PAT).table(AIRTABLE_BASE_ID, TABLE_NAME)

# --- NEW: THE SAVING FUNCTION ---
def save_to_airtable(char_name, char_desc, char_url):
    try:
        airtable.create({
            "Name": char_name,
            "Description": char_desc,
            "Portrait": [{"url": char_url}]
        })
        st.toast(f"✅ {char_name} saved to Airtable!")
    except Exception as e:
        st.error(f"Error saving: {e}")

# 2. SIDEBAR
with st.sidebar:
    st.header("1. Character Details")
    name = st.text_input("Character Name")
    description = st.text_area("Traits (e.g. blonde man portrait)")
    search_btn = st.button("Find Portraits")

# 3. GALLERY
if search_btn and description:
    # We clean the search to focus on faces
    search_query = "+".join(description.split()[:3]) + "+portrait"
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={search_query}&image_type=photo&per_page=4"
    
    response = requests.get(url).json()
    
    if response.get('hits'):
        st.write(f"### Select a Portrait for **{name}**")
        cols = st.columns(4)
        
        for i, hit in enumerate(response['hits']):
            with cols[i]:
                img_url = hit['webformatURL']
                st.image(img_url, use_container_width=True)
                
                # We use 'on_click' to ensure the data is sent IMMEDIATELY
                st.button(
                    f"Save Option {i+1}", 
                    key=f"btn_{i}", 
                    on_click=save_to_airtable, 
                    args=(name, description, img_url)
                )
    else:
        st.warning("No photos found. Try simpler keywords.")

# 4. LIBRARY VIEW
st.divider()
st.header("📂 Your Character Library")
try:
    records = airtable.all()
    if records:
        lib_cols = st.columns(4)
        for idx, rec in enumerate(records):
            f = rec['fields']
            with lib_cols[idx % 4]:
                with st.container(border=True):
                    if "Portrait" in f:
                        st.image(f["Portrait"][0]["url"], use_container_width=True)
                    st.subheader(f.get("Name", "Unnamed"))
                    st.caption(f.get("Description", "")[:50] + "...")
except:
    pass
