import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline

# Configure page settings
st.set_page_config(
    page_title="AI PDF Summarizer",
    page_icon="📄",
    layout="wide"
)

# Load the summarization model with caching
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="t5-small")

# Main title
st.title("📄 AI PDF Summarizer")
st.subheader("Upload your PDF and get instant AI summaries!")

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# File uploader section
uploaded_file = st.file_uploader(
    "**Choose a PDF file**",
    type="pdf",
    help="Select a PDF file to extract text and generate summaries"
)

# Process uploaded file
if uploaded_file is not None:
    try:
        # Read the PDF file
        pdf_bytes = uploaded_file.read()
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract text from all pages
        full_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document.get_page(page_num)
            full_text += page.get_text()
        
        # Close the PDF document
        pdf_document.close()
          # Check if text was extracted
        if full_text.strip():
            # Add spacing before preview section
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Text preview section
            st.markdown("### 🔍 Extracted Preview")
            
            # Show preview (first 1000 characters)
            preview_text = full_text[:1000]
            if len(full_text) > 1000:
                preview_text += "..."
            
            # Display the preview in a text area for better formatting
            st.text_area(
                "Text Preview:",
                preview_text,
                height=300,
                disabled=True
            )
            
            # Show document statistics
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("**Total Pages**", pdf_document.page_count)
            
            with col2:
                st.metric("**Total Characters**", len(full_text))
            
            with col3:
                st.metric("**Total Words**", len(full_text.split()))
            
            # AI Summarization Section
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🧠 AI Summarization")
            
            # Text to summarize (first 1000 characters)
            text_to_summarize = full_text[:1000]
            
            # Summarize button
            if st.button("🧠 Summarize Text", type="primary", use_container_width=True):
                try:
                    # Show loading spinner
                    with st.spinner("🔄 Generating AI summary..."):
                        # Load the summarizer model
                        summarizer = load_summarizer()
                        
                        # Generate summary
                        summary = summarizer(text_to_summarize, max_length=150, min_length=50, do_sample=False)
                        summary_text = summary[0]['summary_text']
                    
                    # Display the summary result
                    st.markdown("### ✅ Summary Result")
                    st.success(f"📝 **Generated Summary:**\n\n{summary_text}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating summary: {str(e)}")
                    st.info("Please try again or check if the text content is suitable for summarization.")
            
            # Add information about summarization
            st.info("💡 **Note:** The AI will summarize the first 1000 characters of your document for optimal performance.")
            
        else:
            st.error("❌ No text could be extracted from this PDF. The file might be image-based or corrupted.")
            
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        st.info("Please make sure you've uploaded a valid PDF file.")

else:
    # Show instructions when no file is uploaded
    st.info("👆 Please upload a PDF file to get started!")
      # Add some helpful information
    st.markdown("---")
    st.markdown("### ℹ️ How to use:")
    st.markdown("""
    1. **Upload a PDF file** using the file uploader above
    2. **View the extracted text** preview to ensure proper text extraction
    3. **Click "🧠 Summarize Text"** to get an AI-generated summary instantly!
    """)
    
    st.markdown("### 📋 Supported formats:")
    st.markdown("- PDF files (.pdf)")
    st.markdown("- Text-based PDFs work best")
    st.markdown("- Image-based PDFs may not extract text properly")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 14px;'>
        Built with ❤️ using Streamlit | AI PDF Summarizer v1.0
    </div>
    """,
    unsafe_allow_html=True
)
