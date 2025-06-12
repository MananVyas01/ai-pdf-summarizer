# 📄 AI PDF Summarizer with LLMs

A powerful web application that extracts text from PDF documents and generates AI-powered summaries using state-of-the-art language models. Built with Streamlit for an intuitive user experience.

## ✨ Features

- 📤 **Upload PDF documents** - Support for text-based PDF files
- 🔍 **View extracted text preview** (first 1000 characters)
- 🧠 **Summarize using Hugging Face `t5-small` model** - Advanced AI summarization
- 📌 **Summary displayed as clean bullet points** - Easy-to-read format
- 📥 **Download the summary as a `.txt` file** - Save for future reference
- 🖼️ **Polished UI with emoji icons and clear sectioning** - Modern, user-friendly interface
- 📊 **Document statistics** - View page count, word count, and character count
- 🎯 **Expandable sections** - Organized workflow with collapsible panels
- 🔄 **Real-time processing** - Instant text extraction and summarization

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – UI framework for building interactive web apps
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) – PDF text extraction and processing
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) – AI summarization models
- [Torch](https://pytorch.org/) – Backend for transformer models
- [Python](https://python.org/) – Core programming language

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

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 🌐 Live Demo

🚧 Coming soon! Stay tuned for a hosted version on Streamlit Cloud or Hugging Face Spaces.

## 🖼️ Screenshot

![App Screenshot](screenshot.png)

> Replace this placeholder with a real screenshot after UI setup.

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

This project uses the **T5-Small** model from Hugging Face:
- **Model**: `t5-small`
- **Task**: Text-to-text generation (summarization)
- **Parameters**: ~60M parameters
- **Performance**: Optimized for speed and efficiency
- **Caching**: Model is cached using Streamlit's `@st.cache_resource` for faster subsequent runs

## 📋 Supported File Formats

- ✅ **PDF files (.pdf)** - Primary format
- ✅ **Text-based PDFs** - Work best for extraction
- ❌ **Scanned PDFs** - May not extract text properly
- ❌ **Password-protected PDFs** - Not currently supported

## 💡 Tips for Best Results

- Ensure your PDF contains selectable text (not just images)
- Smaller documents (under 50 pages) process faster
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
