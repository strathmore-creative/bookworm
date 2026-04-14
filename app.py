import streamlit as st
import requests
from pyairtable import Api

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="Bookworm", page_icon="📖", layout="wide")

# Load Secrets
try:
    PIXABAY_API_KEY = st.secrets["PIXABAY_API_KEY"]
    AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
    AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
    
    # Initialize Airtable API
    api = Api(AIRTABLE_PAT)
    table_characters = api.table(AIRTABLE_BASE_ID, "Characters")
    table_books = api.table(AIRTABLE_BASE_ID, "Books")
except Exception as e:
    st.error("Secrets or Table names missing! Check Streamlit and Airtable.")
    st.stop()

# --- THE SAVING FUNCTION ---
def save_character(c_name, c_desc, c_url, book_id):
    try:
        table_characters.create({
            "Name": c_name,
            "Description": c_desc,
            "Portrait": [{"url": c_url}],
            "Book Link": [book_id] # This creates the relational link
        })
        st.toast(f"✅ {c_name} saved to the library!")
    except Exception as e:
        st.error(f"Airtable Error: {e}")

# 2. SIDEBAR: DATA INTAKE
with st.sidebar:
    st.header("1. Select Book")
    
    # Fetch existing books to populate the dropdown
    books_data = table_books.all()
    book_options = {rec['fields'].get('Title', 'Untitled'): rec['id'] for rec in books_data}
    
    if not book_options:
        st.warning("Go to Airtable and add a Book to the 'Books' table first!")
        st.stop()
        
    selected_book_name = st.selectbox("Which book are you reading?", options=list(book_options.keys()))
    selected_book_id = book_options[selected_book_name]

    st.divider()
    st.header("2. Character Details")
    char_name = st.text_input("Name", placeholder="e.g., Max Vandenburg")
    char_traits = st.text_area("Traits", placeholder="e.g., thin man, kind eyes, 1940s portrait")
    search_btn = st.button("Find Portraits")

# 3. MAIN GALLERY: SEARCH RESULTS
if search_btn and char_traits:
    # Optimized search query
    clean_query = "+".join(char_traits.split()[:4]) + "+portrait"
    pixabay_url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={clean_query}&image_type=photo&per_page=4"
    
    response = requests.get(pixabay_url).json()
    
    if response.get('hits'):
        st.write(f"### Select a Portrait for **{char_name}** in *{selected_book_name}*")
        cols = st.columns(4)
        
        for i, hit in enumerate(response['hits']):
            with cols[i]:
                img_url = hit['webformatURL']
                st.image(img_url, use_container_width=True)
                
                # The Save Button
                st.button(
                    f"Save Option {i+1}", 
                    key=f"save_{i}", 
                    on_click=save_character, 
                    args=(char_name, char_traits, img_url, selected_book_id)
                )
    else:
        st.warning("No photos found. Try simpler keywords like 'man' or 'woman'.")

# 4. PREVIEW: SHOW THE CAST
st.divider()
st.subheader(f"Current Cast of *{selected_book_name}*")
try:
    # Show only characters linked to the selected book
    all_chars = table_characters.all()
    # Filter for characters where 'Book Link' contains our selected_book_id
    current_cast = [c for c in all_chars if selected_book_id in c['fields'].get('Book Link', [])]
    
    if current_cast:
        cast_cols = st.columns(4)
        for idx, char in enumerate(current_cast):
            with cast_cols[idx % 4]:
                f = char['fields']
                if "Portrait" in f:
                    st.image(f["Portrait"][0]["url"], use_container_width=True)
                st.write(f"**{f.get('Name')}**")
    else:
        st.info("No characters saved for this book yet.")
except:
    pass
