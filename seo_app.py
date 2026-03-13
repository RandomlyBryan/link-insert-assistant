import streamlit as st
import google.generativeai as genai
import difflib

# --- API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("API Key missing in Secrets!")
    st.stop()

# --- APP UI ---
st.title("🔗 SEO Smart Link Inserter (v3.1)")

with st.sidebar:
    st.header("Settings")
    # Updated to the 2026 stable models
    model_choice = st.selectbox(
        "Select Model", 
        ["gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview", "gemini-3-flash-preview"]
    )
    keyword = st.text_input("Anchor Text")
    url = st.text_input("Target URL")

# --- CORE LOGIC ---
article_content = st.text_area("Paste Article", height=400)

if st.button("Generate"):
    try:
        # Prepend 'models/' to ensure the API recognizes the path
        model = genai.GenerativeModel(model_name=f"models/{model_choice}")
        
        prompt = f"""
        Task: Insert a link with anchor text "{keyword}" pointing to "{url}".
        Strategy: Use a bridge sentence like "You can also check {keyword} in our indepth guide" if needed.
        Output: Full article with <a href="{url}">{keyword}</a>.
        
        Article:
        {article_content}
        """
        
        response = model.generate_content(prompt)
        new_content = response.text
        
        # Display Results
        tab1, tab2 = st.tabs(["Preview", "Diff (Changes)"])
        with tab1:
            st.markdown(new_content, unsafe_allow_html=True)
        with tab2:
            diff = difflib.ndiff(article_content.splitlines(), new_content.splitlines())
            st.code("\n".join(list(diff)), language="diff")
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("If you still get a 404, please try 'gemini-3.1-flash-lite-preview' as it has the widest availability.")
