import streamlit as st
import google.generativeai as genai
import difflib

# --- 1. API CONFIGURATION ---
try:
    # Accessing the key from Streamlit Secrets
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("⚠️ API Key not found! Please check your Streamlit Secrets.")
    st.stop()

# --- 2. APP UI SETUP ---
st.set_page_config(page_title="SEO Link Inserter", layout="wide", page_icon="🔗")

st.title("🔗 SEO Smart Link Inserter")
st.markdown("Naturally insert anchor text using Gemini AI with automatic 'bridge sentence' detection.")

# Sidebar for Inputs
with st.sidebar:
    st.header("SEO Parameters")
    keyword = st.text_input("Anchor Text / Keyword", placeholder="e.g., project management tools")
    url = st.text_input("Target URL", placeholder="https://example.com/blog/best-tools")
    
    st.divider()
    st.header("Model Settings")
    # Using specific model IDs to avoid the 404 error
    model_choice = st.selectbox("Select Model", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0)
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    st.info("Flash: Fast & efficient.\nPro: Better for complex writing.")

# Main Interface Layout
col_in, col_out = st.columns(2)

with col_in:
    st.subheader("1. Original Content")
    article_content = st.text_area("Paste your article here...", height=500)

with col_out:
    st.subheader("2. Processed Result")
    
    if st.button("Generate Linked Article", type="primary"):
        if not keyword or not url or not article_content:
            st.warning("Please fill in all fields (Keyword, URL, and Article).")
        else:
            try:
                # FIX: Prepend 'models/' to the choice to match Google's API requirement
                model_id = f"models/{model_choice}"
                model = genai.GenerativeModel(model_name=model_id)
                
                # The SEO Optimization Prompt
                prompt = f"""
                You are a professional SEO Content Editor.
                
                TASK:
                Insert a hyperlink with the exact anchor text "{keyword}" pointing to "{url}" into the article below.
                
                INSTRUCTIONS:
                1. Contextual Fit: Place the link in the most relevant paragraph.
                2. Natural Flow: You may edit an existing sentence OR add a new 'bridge sentence' to make the transition smooth.
                3. Preferred Phrasing: You are encouraged to use phrases like "You can also check {keyword} in our indepth guide" or "For further reading, see our guide on {keyword}."
                4. Output Requirement: Return the FULL article content with the link included as HTML: <a href="{url}">{keyword}</a>.
                
                ARTICLE:
                {article_content}
                """
                
                with st.spinner(f"Gemini is analyzing context..."):
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(temperature=temperature)
                    )
                    new_content = response.text
                    
                    # --- RESULTS TABS ---
                    tab1, tab2, tab3 = st.tabs(["✨ Preview", "🔍 Compare Changes", "📄 HTML Output"])
                    
                    with tab1:
                        # Renders the HTML so you can see the link work
                        st.markdown(new_content, unsafe_allow_html=True)
                    
                    with tab2:
                        st.info("Lines with '+' were added or modified by AI.")
                        # Create a standard 'diff' view to show before vs after
                        diff = difflib.ndiff(article_content.splitlines(), new_content.splitlines())
                        diff_display = "\n".join(list(diff))
                        st.code(diff_display, language="diff")
                    
                    with tab3:
                        # Raw HTML for easy copy-pasting into Webflow/WordPress
                        st.code(new_content, language="html")
                        st.download_button(
                            label="Download HTML File",
                            data=new_content,
                            file_name="linked_article.html",
                            mime="text/html"
                        )
                        
            except Exception as e:
                st.error(f"Error: {e}")
                if "404" in str(e):
                    st.info("Tip: If you see a 404, try switching the model in the sidebar.")
    else:
        st.info("Enter your article details and click 'Generate' to see the changes side-by-side.")
