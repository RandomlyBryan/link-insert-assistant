import streamlit as st
import google.generativeai as genai
import difflib

# --- 1. API CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("⚠️ API Key not found in Secrets!")
    st.stop()

# --- 2. APP UI ---
st.set_page_config(page_title="SEO Link Inserter", layout="wide", page_icon="🔗")
st.title("🔗 SEO Smart Link Inserter")

with st.sidebar:
    st.header("SEO Parameters")
    keyword = st.text_input("Anchor Text", placeholder="e.g., best task manager")
    url = st.text_input("Target URL", placeholder="https://example.com")
    
    st.divider()
    st.header("Model Settings")
    model_choice = st.selectbox("Select Model", ["gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview"], index=0)
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

col_in, col_out = st.columns(2)

with col_in:
    st.subheader("1. Original Content")
    article_content = st.text_area("Paste article here...", height=500)

with col_out:
    st.subheader("2. Changes Only")
    if st.button("Generate Linked Article", type="primary"):
        if not keyword or not url or not article_content:
            st.warning("Please fill in all fields.")
        else:
            try:
                model_id = f"models/{model_choice}"
                model = genai.GenerativeModel(model_name=model_id)
                
                prompt = f"""
                Task: Insert a hyperlink with anchor text "{keyword}" pointing to "{url}".
                Strategy: Use a bridge sentence like "You can also check {keyword} in our indepth guide" if no natural fit exists.
                Output: Return the FULL article with the link as <a href="{url}">{keyword}</a>.
                
                ARTICLE:
                {article_content}
                """
                
                with st.spinner("AI is analyzing..."):
                    response = model.generate_content(prompt)
                    new_content = response.text
                    
                    tab1, tab2, tab3 = st.tabs(["🔍 Just the Changes", "✨ Full Preview", "📄 HTML"])
                    
                    with tab1:
                        # n=3 means 3 lines of context around the change
                        diff = difflib.context_diff(
                            article_content.splitlines(keepends=True), 
                            new_content.splitlines(keepends=True), 
                            fromfile='Before', tofile='After', n=2
                        )
                        diff_text = "".join(diff)
                        
                        if diff_text:
                            st.write("Below is only the section where the link was added:")
                            st.code(diff_text, language="diff")
                        else:
                            st.info("No changes detected by the AI.")
                    
                    with tab2:
                        st.markdown(new_content, unsafe_allow_html=True)
                    
                    with tab3:
                        st.code(new_content, language="html")
                        st.download_button("Download HTML", new_content, file_name="seo_article.html")
                        
            except Exception as e:
                st.error(f"Error: {e}")
