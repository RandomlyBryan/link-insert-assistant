import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
# Replace with your actual Gemini API Key or use streamlit secrets
GEMINI_API_KEY = "AIzaSyBiNIVc4Kv-ak8V_X7bs3kOx2LXU_NabEU"
genai.configure(api_key=AIzaSyBiNIVc4Kv-ak8V_X7bs3kOx2LXU_NabEU)

# --- APP UI ---
st.set_page_config(page_title="SEO Link Inserter", layout="wide")

st.title("🔗 AI-Powered SEO Link Inserter")
st.markdown("Naturally insert anchor text into your articles without breaking the flow.")

# Sidebar for Inputs
with st.sidebar:
    st.header("Project Details")
    keyword = st.text_input("Anchor Text / Keyword", placeholder="e.g., cloud security")
    url = st.text_input("Target URL", placeholder="https://example.com/blog")
    
    st.divider()
    st.header("Settings")
    model_choice = st.selectbox("Select Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)

# Main Area
col1, col2 = st.columns(2)

with col1:
    st.subheader("Original Article")
    article_content = st.text_area("Paste your article here...", height=500)

with col2:
    st.subheader("Processed Article")
    if st.button("Generate Linked Article"):
        if not keyword or not url or not article_content:
            st.error("Please provide the keyword, URL, and article content.")
        else:
            try:
                # Initialize Gemini
                model = genai.GenerativeModel(model_name=model_choice)
                
                # The Prompt Strategy
                prompt = f"""
                You are an SEO Content Editor. Your goal is to insert a hyperlink into the article below.
                
                TARGET:
                - Anchor Text: {keyword}
                - URL: {url}
                
                INSTRUCTIONS:
                1. Insert the link naturally. Do not just drop it in randomly.
                2. If the keyword fits an existing sentence, rewrite that sentence slightly to include it.
                3. If it doesn't fit naturally, you MUST add a 'bridge sentence' or a call-to-action.
                4. You are encouraged to use phrases like: "You can also check {keyword} in our indepth guide" or similar natural variations.
                5. The final output must be the FULL article.
                6. Wrap the keyword in an HTML anchor tag: <a href="{url}">{keyword}</a>.
                
                ARTICLE:
                {article_content}
                """
                
                with st.spinner("Gemini is rewriting..."):
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=temperature
                        )
                    )
                    
                    # Displaying the result
                    st.markdown(response.text, unsafe_allow_html=True)
                    
                    # Provide raw HTML for easy copying
                    st.divider()
                    st.caption("Raw HTML Output:")
                    st.code(response.text, language="html")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.info("Click 'Generate' to see the result here.")