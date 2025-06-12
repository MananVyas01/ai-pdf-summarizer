import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
from datetime import datetime
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import io

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
def load_summarizer(model_name="t5-small"):
    return pipeline("summarization", model=model_name)

# Check if Tesseract is available
@st.cache_data
def check_tesseract():
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

# Text chunking function for large documents
def chunk_text(text, chunk_size=1000):
    """Break text into smaller chunks for processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        if current_length + word_length > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# Enhanced summarization for chunked text
def summarize_chunked_text(text, summarizer, chunk_size=1000, detail_level="Detailed"):
    """Summarize large text by processing it in chunks with enhanced detail preservation"""
    if not text.strip():
        return "No text available for summarization."
    
    chunks = chunk_text(text, chunk_size)
    total_chunks = len(chunks)
    
    # Adjust parameters based on detail level and document size
    if detail_level == "Brief":
        max_per_chunk = 80
        min_per_chunk = 20
        final_max = 250
    elif detail_level == "Detailed":
        max_per_chunk = 150
        min_per_chunk = 40
        final_max = 400
    else:  # Comprehensive
        max_per_chunk = 200
        min_per_chunk = 50
        final_max = 600
    
    # For very large documents, preserve more detail
    if total_chunks > 10:
        max_per_chunk = int(max_per_chunk * 1.3)
        final_max = int(final_max * 1.5)
    
    if len(chunks) == 1:
        # Single chunk - direct summarization with enhanced length
        try:
            summary = summarizer(text, max_length=final_max, min_length=min_per_chunk * 2, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    # Multiple chunks - process each chunk with progress tracking
    chunk_summaries = []
    
    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 30:  # Skip very short chunks
            continue
        try:
            # Update progress if we have access to streamlit
            if 'st' in globals():
                progress = int(30 + (i / total_chunks) * 50)  # 30-80% progress range
                st.session_state.get('progress_bar', lambda x: None)(progress)
                st.session_state.get('status_text', lambda x: None)(f"🧩 Processing chunk {i+1}/{total_chunks}...")
            
            # Summarize each chunk with appropriate length
            summary = summarizer(chunk, max_length=max_per_chunk, min_length=min_per_chunk, do_sample=False)
            chunk_summaries.append(summary[0]['summary_text'])
            
        except Exception as e:
            if 'st' in globals():
                st.warning(f"Warning: Could not summarize chunk {i+1}: {str(e)}")
            continue
    
    if not chunk_summaries:
        return "Unable to generate summary from the provided text."
    
    # Combine all chunk summaries
    combined_summary = " ".join(chunk_summaries)
    
    # Only compress if significantly too long, preserve more content
    compression_threshold = final_max * 2  # More generous threshold
    
    if len(combined_summary) > compression_threshold:
        try:
            # Split into paragraphs for better compression
            paragraphs = [s.strip() for s in combined_summary.split('.') if s.strip()]
            
            # Keep more important sentences (longer ones typically have more content)
            important_sentences = sorted(paragraphs, key=len, reverse=True)
            
            # Take top sentences up to our limit
            final_content = []
            current_length = 0
            
            for sentence in important_sentences:
                if current_length + len(sentence) < compression_threshold:
                    final_content.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            # Reorder by original appearance for better flow
            final_summary_text = '. '.join(final_content)
            
            # Final AI compression if still too long
            if len(final_summary_text) > final_max:
                final_summary = summarizer(final_summary_text, max_length=final_max, min_length=final_max//2, do_sample=False)
                return final_summary[0]['summary_text']
            
            return final_summary_text
            
        except Exception as e:
            if 'st' in globals():
                st.warning(f"Final compression failed: {str(e)}")
            return combined_summary
    
    return combined_summary

# Format summary into bullet points
def format_summary_bullets(summary_text):
    """Format summary text into clean bullet points with enhanced extraction"""
    if not summary_text.strip():
        return ["No summary content available"]
    
    # Multiple splitting strategies to capture more content
    bullet_points = []
    
    # Strategy 1: Split by periods and common conjunctions
    sentences = []
    for delimiter in ['. ', '; ', ', and ', ', but ', ', however ', ', therefore ', ', furthermore ']:
        if delimiter in summary_text:
            parts = summary_text.split(delimiter)
            sentences.extend([p.strip() for p in parts if p.strip()])
            break
    
    # If no good splits found, split by periods only
    if not sentences:
        sentences = [s.strip() for s in summary_text.split('.') if s.strip()]
    
    # Strategy 2: Also look for natural breaks like "Additionally", "Moreover", etc.
    enhanced_sentences = []
    for sentence in sentences:
        # Split on transition words that indicate new points
        for transition in [' Additionally', ' Moreover', ' Furthermore', ' Also', ' In addition', ' Another']:
            if transition in sentence:
                parts = sentence.split(transition)
                enhanced_sentences.extend([p.strip() for p in parts if p.strip()])
                break
        else:
            enhanced_sentences.append(sentence)
    
    # Clean and filter sentences
    for sentence in enhanced_sentences:
        sentence = sentence.strip()
        
        # Skip very short phrases or incomplete thoughts
        if len(sentence.split()) < 4:
            continue
            
        # Clean up the sentence
        # Remove leading conjunctions and transitions
        for prefix in ['and ', 'but ', 'however ', 'therefore ', 'furthermore ', 'additionally ', 'moreover ', 'also ']:
            if sentence.lower().startswith(prefix):
                sentence = sentence[len(prefix):].strip()
                break
        
        # Remove trailing period if exists
        if sentence.endswith('.'):
            sentence = sentence[:-1]
        
        # Ensure sentence starts with capital letter
        if sentence and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        
        # Only add if it's meaningful (has substance)
        if len(sentence) > 10 and any(word in sentence.lower() for word in 
                                     ['the', 'is', 'are', 'was', 'were', 'have', 'has', 'will', 'can', 'should']):
            bullet_points.append(sentence)
    
    # If we still don't have enough points, try a different approach
    if len(bullet_points) < 3:
        # Split by commas for more granular points
        comma_split = [s.strip() for s in summary_text.split(',') if len(s.strip().split()) >= 5]
        for point in comma_split[:10]:  # Limit to prevent too many small points
            if point not in bullet_points:
                # Clean and format
                point = point.strip()
                if point.endswith('.'):
                    point = point[:-1]
                if point and point[0].islower():
                    point = point[0].upper() + point[1:]
                bullet_points.append(point)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_points = []
    for point in bullet_points:
        # Simple similarity check - avoid very similar points
        point_words = set(point.lower().split())
        is_duplicate = False
        for seen_point in seen:
            seen_words = set(seen_point.lower().split())
            if len(point_words.intersection(seen_words)) / max(len(point_words), len(seen_words)) > 0.7:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_points.append(point)
            seen.add(point)
    
    return unique_points[:20]  # Limit to top 20 points to avoid overwhelming UI

# Sidebar Panel
st.sidebar.title("📄 AI PDF Summarizer")
st.sidebar.markdown("Summarize PDF documents instantly using AI – upload, preview, and generate insights in seconds.")
st.sidebar.markdown("---")

# Model selection
st.sidebar.markdown("### 🤖 AI Model Selection")
model_choice = st.sidebar.selectbox(
    "Choose Summarization Model:",
    ["t5-small", "facebook/bart-large-cnn"],
    help="T5-small is faster, BART-large-cnn provides better quality"
)
st.sidebar.markdown("---")

st.sidebar.markdown("### 📋 Enhanced Features")
st.sidebar.markdown("• **Advanced PDF Text Extraction** - Extract from any PDF type")
st.sidebar.markdown("• **Smart OCR Fallback** - Handle scanned/image-based PDFs")
st.sidebar.markdown("• **Chunked AI Summarization** - Process documents of any size")
st.sidebar.markdown("• **Detail Preservation** - Maintain comprehensive content coverage")
st.sidebar.markdown("• **Smart Bullet Points** - Clean, organized summary format")
st.sidebar.markdown("• **Document Analytics** - Detailed statistics and metrics")
st.sidebar.markdown("• **Enhanced Downloads** - Comprehensive summary reports")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Technology Stack")
st.sidebar.markdown("• **Streamlit** - Web interface")
st.sidebar.markdown("• **PyMuPDF** - PDF processing")
st.sidebar.markdown("• **Tesseract OCR** - Image text extraction")
st.sidebar.markdown("• **pdf2image** - PDF to image conversion")
st.sidebar.markdown("• **Transformers** - AI summarization")
st.sidebar.markdown("• **T5-Small Model** - Natural language processing")
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 *Crafted with ❤️ by Manan Vyas*")

# Main title
st.title("📄 AI PDF Summarizer")
st.subheader("Upload your PDF and get instant AI summaries!")
st.caption("💡 Tip: This app works with both text-based and scanned PDFs. OCR will automatically activate for image-based documents.")
st.warning("⚠️ Note: This summarizer may provide less comprehensive summaries than desired because it currently uses a small model. API integration with more powerful models is coming soon — stay tuned!")

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# File uploader section in expandable container
with st.expander("📤 Upload Your PDF", expanded=True):
    uploaded_file = st.file_uploader(
        "**Choose a PDF file**",
        type="pdf",
        help="Select a PDF file to extract text and generate summaries"
    )
    st.info("📌 **Supported formats:** PDF files (.pdf) - Both text-based and scanned/image-based PDFs supported with OCR fallback")

# Process uploaded file
if uploaded_file is not None:
    try:
        # Read the PDF file
        pdf_bytes = uploaded_file.read()
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract text from all pages (Primary method)
        full_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]  # Updated API method
            full_text += page.get_text()
        
        # Store page count before closing document
        total_pages = pdf_document.page_count
          # Close the PDF document
        pdf_document.close()
        
        # OCR Fallback for image-based/scanned PDFs
        ocr_used = False
        if not full_text.strip():
            if check_tesseract():
                st.warning("⚠️ No extractable text found — attempting OCR fallback for scanned/image-based PDF.")
                
                try:
                    with st.spinner("🔍 Running OCR on scanned pages... This may take a moment."):
                        # Convert PDF pages to images
                        uploaded_file.seek(0)  # Reset file pointer
                        pdf_bytes = uploaded_file.read()
                        images = convert_from_bytes(pdf_bytes)
                        
                        # Extract text using OCR
                        full_text = ""
                        for i, image in enumerate(images):
                            st.progress((i + 1) / len(images), text=f"Processing page {i + 1}/{len(images)}")
                            page_text = pytesseract.image_to_string(image)
                            full_text += page_text + "\n"
                        
                        ocr_used = True
                        st.success(f"✅ OCR completed! Extracted text from {len(images)} page(s).")
                        
                except Exception as ocr_error:
                    st.error(f"❌ OCR processing failed: {str(ocr_error)}")
                    st.info("Please ensure the PDF contains readable text or images.")
                    full_text = ""
            else:
                st.error("❌ No extractable text found and OCR is not available.")
                st.info("📋 **To enable OCR support:**\n- Install Tesseract OCR binary\n- Windows: Download from GitHub releases\n- Linux/Mac: Use package manager (apt/brew)")
                full_text = ""
        
        # Check if text was extracted
        if full_text.strip():
            # Extracted Preview Section
            with st.expander("🔍 Extracted Preview (First 1000 Characters)", expanded=True):
                if ocr_used:
                    st.markdown("### 📖 Document Text Preview (OCR Extracted)")
                    st.info("ℹ️ **Note:** Text was extracted using OCR. Accuracy may vary based on image quality.")
                else:
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
                
                # Show document processing information
                word_count = len(full_text.split())
                char_count = len(full_text)
                estimated_chunks = max(1, char_count // 1000)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 **Document Size:** {word_count:,} words, {char_count:,} characters")
                with col2:
                    st.info(f"🧩 **Processing:** Will be divided into ~{estimated_chunks} chunks for comprehensive analysis")
                
                if ocr_used:
                    st.warning("⚠️ **OCR Note:** Text was extracted using OCR. Summary quality depends on OCR accuracy.")
                  # Summary length selection
                st.markdown("### ⚙️ Enhanced Summary Settings")
                summary_detail = st.select_slider(
                    "Choose summary detail level:",
                    options=["Brief", "Detailed", "Comprehensive"],
                    value="Detailed",
                    help="Brief: ~5-8 key points | Detailed: ~10-15 points | Comprehensive: ~15-25+ points with maximum detail preservation"
                )
                
                # Show what each level provides
                detail_info = {
                    "Brief": "🎯 **Brief**: Captures main themes and key conclusions (fastest processing)",
                    "Detailed": "📋 **Detailed**: Balanced coverage of important points and supporting details",
                    "Comprehensive": "📚 **Comprehensive**: Maximum detail retention with extensive coverage of all topics"
                }
                st.info(detail_info[summary_detail])
                
                # Summarize button
                if st.button("🧠 Generate Comprehensive Summary", type="primary", use_container_width=True):
                    try:
                        # Show loading spinner with progress
                        with st.spinner("🔄 Generating comprehensive AI summary... This may take a moment for large documents."):
                            # Load the summarizer model with selected model
                            summarizer = load_summarizer(model_choice)
                            
                            # Progress bar
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                              # Update progress: Starting
                            progress_bar.progress(10)
                            status_text.text("📝 Analyzing document structure...")
                            
                            # Store progress components in session state for chunk processing
                            st.session_state['progress_bar'] = progress_bar.progress
                            st.session_state['status_text'] = status_text.text
                            
                            # Generate chunked summary with dynamic chunk sizing
                            # Smaller chunks for more detailed summaries
                            if summary_detail == "Brief":
                                chunk_size = 1200  # Larger chunks, fewer summaries
                            elif summary_detail == "Detailed":
                                chunk_size = 900   # Medium chunks, balanced
                            else:  # Comprehensive
                                chunk_size = 700   # Smaller chunks, more detailed coverage
                            
                            progress_bar.progress(30)
                            status_text.text("🧩 Breaking document into optimal chunks...")
                            
                            # Get comprehensive summary with detail level
                            comprehensive_summary = summarize_chunked_text(full_text, summarizer, chunk_size, summary_detail)
                            
                            progress_bar.progress(80)
                            status_text.text("✨ Formatting final summary...")
                            
                            # Format into bullet points
                            bullet_points = format_summary_bullets(comprehensive_summary)
                            
                            progress_bar.progress(100)
                            status_text.text("✅ Summary complete!")
                            
                            # Clear progress indicators
                            progress_bar.empty()
                            status_text.empty()
                        
                        # Display the summary result with enhanced formatting
                        with st.container():
                            # Add divider for visual separation
                            st.markdown("---")
                            
                            # Header for summary section
                            st.markdown("### 📝 Comprehensive Summary Results")
                              # Summary statistics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Summary Points", len(bullet_points))
                            with col2:
                                compression_ratio = len(full_text) // max(len(comprehensive_summary), 1)
                                st.metric("🔄 Compression Ratio", f"{compression_ratio}:1")
                            with col3:
                                st.metric("🤖 Model Used", model_choice.split('/')[-1])
                            
                            # Additional metrics row
                            col4, col5, col6 = st.columns(3)
                            with col4:
                                st.metric("📝 Summary Length", f"{len(comprehensive_summary)} chars")
                            with col5:
                                st.metric("📄 Original Length", f"{len(full_text)} chars")
                            with col6:
                                coverage_percent = min(100, (len(comprehensive_summary) / len(full_text)) * compression_ratio * 10)
                                st.metric("📈 Content Coverage", f"{coverage_percent:.1f}%")
                            
                            st.markdown("---")
                            
                            # Display bullet points in styled container
                            if bullet_points:
                                bullet_points_html = ""
                                for i, point in enumerate(bullet_points, 1):
                                    bullet_points_html += f"<div style='margin-bottom: 8px;'><strong>{i}.</strong> {point}</div>"
                                
                                st.markdown(
                                    f"""
                                    <div style="background-color:#f0f2f6; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #4CAF50;">
                                        <div style="color: #333; line-height: 1.8; font-size: 16px;">
                                            {bullet_points_html}
                                        </div>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                            else:
                                st.error("❌ Could not generate meaningful bullet points from the summary.")
                                # Fallback: show raw summary
                                st.text_area("Raw Summary:", comprehensive_summary, height=200)
                            
                            # Add success indicator
                            st.success(f"✅ Comprehensive summary generated successfully! ({len(bullet_points)} key points extracted)")
                            
                            # Download section
                            st.markdown("---")
                            st.markdown("### 📥 Download Summary")
                            
                            # Optional: Allow users to customize filename
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                filename = st.text_input(
                                    "Customize filename (optional):",
                                    value="comprehensive_summary",
                                    help="Enter filename without extension (.txt will be added automatically)"
                                )
                            
                            with col2:
                                st.markdown("<br>", unsafe_allow_html=True)  # Add spacing for alignment
                                  # Create downloadable content - convert bullet points to plain text
                                compression_ratio = len(full_text) // max(len(comprehensive_summary), 1)
                                coverage_percent = min(100, (len(comprehensive_summary) / len(full_text)) * compression_ratio * 10)
                                
                                download_content = f"""AI PDF Comprehensive Summary - Enhanced Analysis
{'='*70}

Generated on: {st.session_state.get('current_date', 'Today')}
Document: {uploaded_file.name}
AI Model: {model_choice}
Summary Detail Level: {summary_detail}
Processing Method: Chunked Summarization with Enhanced Detail Preservation

Document Analysis:
- Total Pages: {total_pages}
- Total Words: {word_count:,}
- Total Characters: {char_count:,}
- Estimated Reading Time: {word_count // 200} minutes

Summary Statistics:
- Summary Points Extracted: {len(bullet_points)}
- Summary Length: {len(comprehensive_summary):,} characters
- Compression Ratio: {compression_ratio}:1
- Content Coverage: {coverage_percent:.1f}%
- Chunks Processed: ~{max(1, char_count // chunk_size)}

COMPREHENSIVE SUMMARY:
{'-'*50}
"""
                                
                                # Convert bullet points back to clean text for download
                                for i, point in enumerate(bullet_points, 1):
                                    download_content += f"{i}. {point}\n\n"
                                
                                # Add the full summary text as well
                                download_content += f"""

FULL SUMMARY TEXT:
{'-'*50}
{comprehensive_summary}

{'-'*70}
Generated by AI PDF Summarizer v3.0 - Stage 9 Enhanced
Advanced Chunked Summarization with Detail Preservation
"""
                                
                                # Download button
                                st.download_button(
                                    label="📥 Download Comprehensive Summary",
                                    data=download_content,
                                    file_name=f"{filename}.txt",
                                    mime="text/plain",
                                    type="secondary",
                                    use_container_width=True
                                )
                            
                            st.caption("💡 This comprehensive summary covers the entire document, not just the first 1000 characters.")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating summary: {str(e)}")
                        st.info("Please try again or try with a different model. For very large documents, processing may take longer.")
            
        else:
            st.error("❌ No text could be extracted from this PDF using either direct extraction or OCR.")
            st.info("🔧 **Possible reasons:**\n- The PDF contains only non-text images\n- The image quality is too poor for OCR\n- The PDF is corrupted or password-protected\n- OCR dependencies may not be properly installed")
            
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        st.info("Please make sure you've uploaded a valid PDF file and that all dependencies are installed.")

else:
    # Show instructions when no file is uploaded
    with st.container():
        st.info("👆 Please upload a PDF file to get started!")
        
        # Add helpful information in organized sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ℹ️ How to Use")
            st.markdown("""            1. **📤 Upload a PDF file** using the file uploader above
            2. **🔍 View the extracted text** preview to ensure proper text extraction
            3. **🧠 Click "Generate Comprehensive Summary"** to get an AI-generated summary instantly!
            """)
        
        with col2:
            st.markdown("### 📋 Supported Formats")
            st.markdown("""
            • **PDF files (.pdf)** - Primary format
            • **Text-based PDFs** - Direct text extraction
            • **Scanned/Image PDFs** - OCR text extraction
            • **Mixed content PDFs** - Automatic detection & processing
            • **Password-protected** - Not currently supported
            """)
          # Additional tips section
        st.markdown("---")
        st.markdown("### 💡 Tips for Best Results")
        st.markdown("""
        - **Text-based PDFs**: Fastest processing with highest accuracy
        - **Scanned PDFs**: OCR will activate automatically (may take longer)
        - **Image quality**: Higher resolution scans produce better OCR results
        - **Document size**: Smaller documents process faster
        - **Mixed PDFs**: App automatically detects and uses best extraction method
        - **Complex layouts**: May require manual review of extracted text
        """)

# Footer
st.markdown("---")
st.markdown(
    """    <div style='text-align: center; color: #666; font-size: 14px; margin-top: 50px;'>
        <p>🚀 <strong>AI PDF Summarizer v3.0</strong> | Enhanced with Chunked Summarization | Built with ❤️ using Streamlit</p>
        <p>📧 Questions or feedback? Reach out to <strong>Manan Vyas</strong></p>
    </div>
    """,
    unsafe_allow_html=True
)
