import streamlit as st
import google.generativeai as genai
import difflib

# --- 1. API CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key not found! Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- 2. APP UI SETUP ---
st.set_page_config(page_title="SEO Link Inserter", layout="wide", page_icon="🔗")

st.title("🔗 SEO Smart Link Inserter")

# Sidebar for SEO Details
with st.sidebar:
    st.header("SEO Parameters")
    keyword = st.text_input("Anchor Text / Keyword", placeholder="e.g., project management tools")
    url = st.text_input("Target URL", placeholder="https://example.com/blog/best-tools")
    
    st.divider()
    st.header("Model Settings")
    model_choice = st.selectbox("Select Model", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0)
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

# Main Interface
col_in, col_out = st.columns(2)

with col_in:
    st.subheader("Original Content")
    article_content = st.text_area("Paste your article here...", height=400)

with col_out:
    st.subheader("Processed Result")
    generate_btn = st.button("Generate Linked Article", type="primary")

if generate_btn:
    if not keyword or not url or not article_content:
        st.warning("Please fill in all fields.")
    else:
        try:
            model = genai.GenerativeModel(model_name=model_choice)
            
            prompt = f"""
            You are an expert SEO Content Editor.
            TASK: Insert a hyperlink with anchor text "{keyword}" pointing to "{url}" into the article.
            
            STRATEGY:
            1. Find a natural spot or create a 'bridge sentence' like "You can also check {keyword} in our indepth guide."
            2. Return the FULL article.
            3. Use HTML for the link: <a href="{url}">{keyword}</a>.
            
            ARTICLE:
            {article_content}
            """
            
            with st.spinner("Gemini is rewriting..."):
                response = model.generate_content(prompt)
                new_content = response.text

                # --- 3. SHOW CHANGES (BEFORE & AFTER) ---
                st.tabs_list = st.tabs(["✨ Final Preview", "🔍 Compare Changes", "📄 Raw HTML"])
                
                with st.tabs_list[0]:
                    st.markdown(new_content, unsafe_allow_html=True)
                
                with st.tabs_list[1]:
                    st.write("Lines marked with **+** are additions/changes:")
                    # Generate a simple diff
                    diff = difflib.ndiff(article_content.splitlines(), new_content.splitlines())
                    diff_text = "\n".join(list(diff))
                    st.code(diff_text)
                
                with st.tabs_list[2]:
                    st.code(new_content, language="html")
                    st.download_button("Download HTML", new_content, file_name="article.html")
                    
        except Exception as e:
            st.error(f"Error: {e}")
