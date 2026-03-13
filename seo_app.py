import streamlit as st
import google.generativeai as genai
import difflib

# --- 1. API CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("⚠️ API Key not found! Please check your Streamlit Secrets.")
    st.stop()

# --- 2. DYNAMIC MODEL FETCHING ---
# This prevents 404 errors by only showing models your key actually supports.
@st.cache_resource
def get_available_models():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Clean up names for the dropdown (remove 'models/' prefix for display)
        return [m.replace('models/', '') for m in models]
    except Exception as e:
        return ["gemini-3-flash", "gemini-3-pro", "gemini-1.5-flash"]

available_models = get_available_models()

# --- 3. APP UI SETUP ---
st.set_page_config(page_title="SEO Link Inserter", layout="wide", page_icon="🔗")
st.title("🔗 SEO Smart Link Inserter")

with st.sidebar:
    st.header("SEO Parameters")
    keyword = st.text_input("Anchor Text / Keyword", placeholder="e.g., best hiking boots")
    url = st.text_input("Target URL", placeholder="https://example.com/hiking-gear")
    
    st.divider()
    st.header("Model Settings")
    # Dynamic selection to avoid 404
    model_choice = st.selectbox("Select Available Model", available_models)
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    st.info("If you still see a 404, try 'gemini-3-flash' if available.")

# Main Interface
col_in, col_out = st.columns(2)

with col_in:
    st.subheader("1. Original Content")
    article_content = st.text_area("Paste article here...", height=500)

with col_out:
    st.subheader("2. Processed Result")
    if st.button("Generate Linked Article", type="primary"):
        if not keyword or not url or not article_content:
            st.warning("Please fill in all fields.")
        else:
            try:
                # Always prepend 'models/' for the API call
                model_id = f"models/{model_choice}" if not model_choice.startswith("models/") else model_choice
                model = genai.GenerativeModel(model_name=model_id)
                
                prompt = f"""
                You are an SEO Editor. Insert a hyperlink with anchor text "{keyword}" pointing to "{url}".
                
                Rules:
                1. Use a bridge sentence like "You can also check {keyword} in our indepth guide" if no natural fit exists.
                2. Return the ENTIRE article.
                3. Use HTML: <a href="{url}">{keyword}</a>.
                
                ARTICLE:
                {article_content}
                """
                
                with st.spinner("Rewriting with AI..."):
                    response = model.generate_content(prompt)
                    new_content = response.text
                    
                    tab1, tab2, tab3 = st.tabs(["✨ Preview", "🔍 Compare Changes", "📄 HTML Source"])
                    
                    with tab1:
                        st.markdown(new_content, unsafe_allow_html=True)
                    with tab2:
                        diff = difflib.ndiff(article_content.splitlines(), new_content.splitlines())
                        st.code("\n".join(list(diff)), language="diff")
                    with tab3:
                        st.code(new_content, language="html")
                        st.download_button("Download HTML", new_content, file_name="article.html")
            except Exception as e:
                st.error(f"Error: {e}")
