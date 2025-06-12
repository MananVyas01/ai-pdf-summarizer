import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
from datetime import datetime

# Configure page settings
st.set_page_config(
    page_title="AI PDF Summarizer",
    page_icon="📄",
    layout="wide"
)

# Initialize session state for current date
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

# Load the summarization model with caching
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="t5-small")

# Sidebar Panel
st.sidebar.title("📄 AI PDF Summarizer")
st.sidebar.markdown("Summarize PDF documents instantly using AI – upload, preview, and generate insights in seconds.")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Features")
st.sidebar.markdown("• **PDF Text Extraction** - Extract text from any PDF")
st.sidebar.markdown("• **AI-Powered Summarization** - Get key insights instantly")
st.sidebar.markdown("• **Clean Bullet Points** - Easy-to-read summary format")
st.sidebar.markdown("• **Document Statistics** - View page count, word count, etc.")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Technology Stack")
st.sidebar.markdown("• **Streamlit** - Web interface")
st.sidebar.markdown("• **PyMuPDF** - PDF processing")
st.sidebar.markdown("• **Transformers** - AI summarization")
st.sidebar.markdown("• **T5-Small Model** - Natural language processing")
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 *Crafted with ❤️ by Manan Vyas*")

# Main title
st.title("📄 AI PDF Summarizer")
st.subheader("Upload your PDF and get instant AI summaries!")
st.caption("💡 Tip: This app works best with text-based PDFs. Image-based PDFs may not extract text properly.")

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# File uploader section in expandable container
with st.expander("📤 Upload Your PDF", expanded=True):
    uploaded_file = st.file_uploader(
        "**Choose a PDF file**",
        type="pdf",
        help="Select a PDF file to extract text and generate summaries"
    )
    st.info("📌 **Supported formats:** PDF files (.pdf) - Text-based PDFs work best")

# Process uploaded file
if uploaded_file is not None:
    try:
        # Read the PDF file
        pdf_bytes = uploaded_file.read()
          # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")        # Extract text from all pages
        full_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]  # Updated API method
            full_text += page.get_text()
        
        # Store page count before closing document
        total_pages = pdf_document.page_count
        
        # Close the PDF document
        pdf_document.close()
        
        # Check if text was extracted
        if full_text.strip():
            # Extracted Preview Section
            with st.expander("🔍 Extracted Preview (First 1000 Characters)", expanded=True):
                st.markdown("### 📖 Document Text Preview")
                
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
                st.markdown("### 📊 Document Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("**Total Pages**", total_pages)
                
                with col2:
                    st.metric("**Total Characters**", len(full_text))
                
                with col3:
                    st.metric("**Total Words**", len(full_text.split()))
            
            # AI Summarization Section
            with st.expander("🧠 AI-Generated Summary", expanded=True):
                st.markdown("### 🤖 Generate AI Summary")
                st.info("💡 **Note:** The AI will summarize the first 1000 characters of your document for optimal performance.")
                
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
                        
                        # Display the summary result with enhanced formatting
                        with st.container():
                            # Add divider for visual separation
                            st.markdown("---")
                            
                            # Header for summary section
                            st.markdown("### 📝 Key Summary Points")
                            
                            # Convert summary to bullet points
                            summary_points = summary_text.split('. ')
                            
                            # Create styled container for bullet points
                            bullet_points_html = ""
                            for point in summary_points:
                                point = point.strip()
                                # Skip very short or meaningless lines (under 3 words)
                                if len(point.split()) >= 3:
                                    # Remove trailing period if it exists
                                    if point.endswith('.'):
                                        point = point[:-1]
                                    bullet_points_html += f"• {point}<br>"
                            
                            # Display bullet points in styled container
                            st.markdown(
                                f"""
                                <div style="background-color:#f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                                    <div style="color: #333; line-height: 1.6;">
                                        {bullet_points_html}
                                    </div>
                                </div>
                                """, 
                                unsafe_allow_html=True                            )
                            
                            # Add success indicator
                            st.success("✅ Summary generated successfully!")
                            
                            # Download section
                            st.markdown("---")
                            st.markdown("### 📥 Download Summary")
                            
                            # Optional: Allow users to customize filename
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                filename = st.text_input(
                                    "Customize filename (optional):",
                                    value="pdf_summary",
                                    help="Enter filename without extension (.txt will be added automatically)"
                                )
                            
                            with col2:
                                st.markdown("<br>", unsafe_allow_html=True)  # Add spacing for alignment
                                
                                # Create downloadable content - convert bullet points to plain text
                                download_content = f"""AI PDF Summary
{'='*50}

Generated on: {st.session_state.get('current_date', 'Today')}
Document: {uploaded_file.name}

Summary:
{'-'*20}
"""
                                
                                # Convert bullet points back to clean text for download
                                for point in summary_points:
                                    point = point.strip()
                                    if len(point.split()) >= 3:
                                        if point.endswith('.'):
                                            point = point[:-1]
                                        download_content += f"• {point}\n"
                                
                                download_content += f"\n{'-'*50}\nGenerated by AI PDF Summarizer v2.0"
                                
                                # Download button
                                st.download_button(
                                    label="📥 Download Summary",
                                    data=download_content,
                                    file_name=f"{filename}.txt",
                                    mime="text/plain",
                                    type="secondary",
                                    use_container_width=True
                                )
                            
                            st.caption("💡 You can download the above summary for future use.")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating summary: {str(e)}")
                        st.info("Please try again or check if the text content is suitable for summarization.")
            
        else:
            st.error("❌ No text could be extracted from this PDF. The file might be image-based or corrupted.")
            
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        st.info("Please make sure you've uploaded a valid PDF file.")

else:
    # Show instructions when no file is uploaded
    with st.container():
        st.info("👆 Please upload a PDF file to get started!")
        
        # Add helpful information in organized sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ℹ️ How to Use")
            st.markdown("""
            1. **📤 Upload a PDF file** using the file uploader above
            2. **🔍 View the extracted text** preview to ensure proper text extraction
            3. **🧠 Click "Summarize Text"** to get an AI-generated summary instantly!
            """)
        
        with col2:
            st.markdown("### 📋 Supported Formats")
            st.markdown("""
            • **PDF files (.pdf)** - Primary format
            • **Text-based PDFs** - Work best for extraction
            • **Scanned PDFs** - May not extract text properly
            • **Password-protected** - Not currently supported
            """)
        
        # Additional tips section
        st.markdown("---")
        st.markdown("### 💡 Tips for Best Results")
        st.markdown("""
        - Ensure your PDF contains selectable text (not just images)
        - Smaller documents (under 50 pages) process faster
        - The AI summarizes the first 1000 characters for optimal performance
        - Complex technical documents may require manual review of summaries
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 14px; margin-top: 50px;'>
        <p>🚀 <strong>AI PDF Summarizer v2.0</strong> | Built with ❤️ using Streamlit</p>
        <p>📧 Questions or feedback? Reach out to <strong>Manan Vyas</strong></p>
    </div>
    """,
    unsafe_allow_html=True
)
