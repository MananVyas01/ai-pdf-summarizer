# 📄 AI PDF Summarizer with LLMs

A powerful web application that extracts text from PDF documents and generates AI-powered summaries using state-of-the-art language models. Built with Streamlit for an intuitive user experience.

## ✨ Features

- 📤 **Upload PDF documents** - Support for both text-based and scanned PDF files
- 🔍 **Smart text extraction** - Direct extraction for text-based PDFs
- 🔍 **OCR fallback support** - Automatic OCR for scanned/image-based PDFs
- 🧠 **Summarize using Hugging Face models** - Choose from T5, BART, Pegasus, DistilBART, and more
- 📌 **Summary displayed as clean bullet points** - Easy-to-read format
- 📥 **Download the summary as a `.txt` file** - Save for future reference
- 🖼️ **Polished UI with emoji icons and clear sectioning** - Modern, user-friendly interface
- 📊 **Document statistics** - View page count, word count, and character count
- 🎯 **Expandable sections** - Organized workflow with collapsible panels
- 🔄 **Real-time processing** - Instant text extraction and summarization
- ⚡ **Automatic detection** - Intelligently chooses best extraction method

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – UI framework for building interactive web apps
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) – PDF text extraction and processing
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) – AI summarization models
- [Torch](https://pytorch.org/) – Backend for transformer models
- [Python](https://python.org/) – Core programming language
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) – Optical character recognition for scanned PDFs
- [pdf2image](https://github.com/Belval/pdf2image) – PDF to image conversion for OCR processing

## 🚀 Setup Instructions

1. **Clone the repo:**
   ```bash
   git clone https://github.com/MananVyas01/ai-pdf-summarizer.git
   cd ai-pdf-summarizer
   ```

2. **Create virtual environment & activate it (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR (for scanned PDF support):**
   
   **Windows:**
   - Download from [GitHub Releases](https://github.com/tesseract-ocr/tesseract/releases)
   - Add to PATH environment variable
   
   **Linux:**
   ```bash
   sudo apt-get install tesseract-ocr poppler-utils
   ```
   
   **macOS:**
   ```bash
   brew install tesseract poppler
   ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and navigate to `http://localhost:8501`

## 🌐 Live Demo

🚧 Coming soon! Stay tuned for a hosted version on Streamlit Cloud or Hugging Face Spaces.

## 🖼️ Screenshot

![App Screenshot](screenshot.png)



## 📚 How to Use

1. **Upload Your PDF**: Click on the "📤 Upload Your PDF" section and select a text-based PDF file
2. **Preview Text**: Review the extracted text in the "🔍 Extracted Preview" section
3. **Generate Summary**: Click the "🧠 Summarize Text" button in the "🧠 AI-Generated Summary" section
4. **Download**: Use the "📥 Download Summary" button to save your summary as a .txt file

## 🎯 Project Structure

```
ai-pdf-summarizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
└── screenshot.png        # UI screenshot (to be added)
```

## 🤖 AI Model Information

This project supports a wide range of Hugging Face summarization models:

- **T5 Family**: `t5-small`, `t5-base`, `t5-large`
- **BART Family**: `facebook/bart-large-cnn`, `sshleifer/distilbart-cnn-12-6`, `philschmid/bart-large-cnn-samsum`
- **Pegasus Family**: `google/pegasus-xsum`, `google/pegasus-cnn_dailymail`, `google/pegasus-multi_news`, `google/pegasus-pubmed`, `google/pegasus-arxiv`

**Model selection is available in the sidebar.**

- **Task**: Text-to-text generation (summarization)
- **Performance**: T5 is fast and efficient, BART and Pegasus provide higher quality for news and scientific text
- **Caching**: Models are cached using Streamlit's `@st.cache_resource` for faster subsequent runs

## 📋 Supported File Formats

- ✅ **PDF files (.pdf)** - Primary format
- ✅ **Text-based PDFs** - Work best for extraction
- ✅ **Scanned PDFs** - OCR extraction available
- ✅ **Image-based PDFs** - Automatic OCR fallback
- ❌ **Password-protected PDFs** - Not currently supported

## 💡 Tips for Best Results

- **Text-based PDFs**: Fastest processing with highest accuracy
- **Scanned PDFs**: OCR will activate automatically (may take longer)
- **Image quality**: Higher resolution scans produce better OCR results
- **Document size**: Smaller documents process faster
- **Mixed PDFs**: App automatically detects and uses best extraction method
- The AI summarizes the first 1000 characters for optimal performance
- Complex technical documents may require manual review of summaries

## 🔧 Development Stages

This project was developed in multiple stages:

- **Stage 1**: PDF upload and text extraction
- **Stage 2**: AI summarization integration
- **Stage 3**: Bullet-point summary formatting
- **Stage 4**: Sidebar and polished layout
- **Stage 5**: Summary download feature
- **Stage 6**: Requirements and deployment setup
- **Stage 7**: Documentation and README
- **Stage 8**: OCR fallback support for scanned PDFs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Manan Vyas**
- GitHub: [@MananVyas01](https://github.com/MananVyas01)
- Project: [AI PDF Summarizer](https://github.com/MananVyas01/ai-pdf-summarizer)

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [Hugging Face](https://huggingface.co/) for providing the T5 model and transformers library
- [PyMuPDF](https://pymupdf.readthedocs.io/) for robust PDF processing capabilities

---

<div align="center">
  <p>🚀 <strong>AI PDF Summarizer v2.0</strong> | Built with ❤️ using Streamlit</p>
  <p>📧 Questions or feedback? Reach out to <strong>Manan Vyas</strong></p>
</div>
