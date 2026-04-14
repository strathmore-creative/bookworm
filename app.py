import streamlit as st
import requests
from pyairtable import Api

# 1. SETUP
st.set_page_config(page_title="Bookworm Studio", page_icon="🎨", layout="wide")

# Custom CSS for "Card" Styling
st.markdown("""
    <style>
    .char-card {
        border-radius: 10px;
        padding: 10px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

try:
    PIXABAY_API_KEY = st.secrets["PIXABAY_API_KEY"]
    AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
    AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
    
    api = Api(AIRTABLE_PAT)
    table_characters = api.table(AIRTABLE_BASE_ID, "Characters")
    table_books = api.table(AIRTABLE_BASE_ID, "Books")
except Exception as e:
    st.error("Setup incomplete. Check your Secrets on Streamlit Cloud.")
    st.stop()

# --- FUNCTIONS ---
def save_character(c_name, c_desc, c_url, book_id):
    table_characters.create({
        "Name": c_name,
        "Description": c_desc,
        "Portrait": [{"url": c_url}],
        "Book Link": [book_id]
    })
    st.toast(f"✨ {c_name} added to the cast!")

# 2. THE TOP NAVIGATION (Book Selector)
books_data = table_books.all()
book_options = {rec['fields'].get('Title', 'Untitled'): rec['id'] for rec in books_data}

if not book_options:
    st.info("Your library is empty. Add a book title in Airtable to begin.")
    st.stop()

st.title("📚 Bookworm Studio")
selected_book_name = st.selectbox("Current Project:", options=list(book_options.keys()))
selected_book_id = book_options[selected_book_name]

st.divider()

# 3. THE LAYOUT (Capture on Left, Gallery on Right)
col_input, col_display = st.columns([1, 2], gap="large")

with col_input:
    st.header("Capture Character")
    char_name = st.text_input("Name")
    char_traits = st.text_area("Physical Traits (for search)", placeholder="e.g. blue eyes, messy hair, 1920s")
    
    if st.button("Search Pixabay"):
        if char_traits:
            query = char_traits.replace(" ", "+") + "+portrait"
            url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&per_page=6"
            results = requests.get(url).json()
            
            if results.get('hits'):
                for i, hit in enumerate(results['hits']):
                    st.image(hit['webformatURL'], use_container_width=True)
                    st.button(f"Save Image {i+1}", key=f"btn_{i}", 
                              on_click=save_character, 
                              args=(char_name, char_traits, hit['webformatURL'], selected_book_id))
                    st.divider()
            else:
                st.warning("No images found. Try broader traits.")

with col_display:
    st.header(f"The Cast of '{selected_book_name}'")
    
    # Fetch characters for this book
    all_chars = table_characters.all()
    current_cast = [c for c in all_chars if selected_book_id in c['fields'].get('Book Link', [])]
    
    if current_cast:
        # Create a grid for the gallery
        grid_cols = st.columns(2)
        for idx, char in enumerate(current_cast):
            with grid_cols[idx % 2]:
                f = char['fields']
                with st.container():
                    if "Portrait" in f:
                        st.image(f["Portrait"][0]["url"], use_container_width=True)
                    st.subheader(f.get("Name", "Unnamed"))
                    st.write(f.get("Description", ""))
                    st.divider()
    else:
        st.info("The cast is empty. Use the sidebar to find your first character.")
