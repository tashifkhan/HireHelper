import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import io
from PyPDF2 import PdfReader
from docx import Document


def generate_answers(
    resume_text,
    role,
    company,
    questions_list,
    word_limit,
    api_key,
    user_company_knowledge="",
    company_research="",
):
    """Generates answers to interview questions based on the resume and inputs."""
    if not questions_list:
        return []

    llm = GoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        api_key=api_key,
    )

    # Build context about the company
    company_context = ""
    if user_company_knowledge.strip():
        company_context += f"\n\nAdditional information about {company}:\n{user_company_knowledge.strip()}"
    if company_research.strip():
        company_context += (
            f"\n\nResearch findings about {company}:\n{company_research.strip()}"
        )

    template = """
    You are an expert interview coach.
    A candidate with this résumé:
    ```
    {resume}
    ```
    is applying for the role of {role} at {company}.{company_context}
    
    Answer the question below in at most {word_limit} words,
    drawing on experiences and skills from the résumé. If relevant company information is available,
    tailor your answer to show how the candidate's experience aligns with the company's needs and culture.
    ---
    Question: {question}
    """

    prompt = PromptTemplate(
        input_variables=[
            "resume",
            "role",
            "company",
            "company_context",
            "question",
            "word_limit",
        ],
        template=template,
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    results = []
    for q in questions_list:
        try:
            answer = chain.run(
                resume=resume_text,
                role=role,
                company=company,
                company_context=company_context,
                question=q,
                word_limit=word_limit,
            )
            results.append({"question": q, "answer": answer})
        except Exception as e:
            results.append({"question": q, "answer": f"Error generating answer: {e}"})
    return results


def process_document(file_bytes, file_name):
    """Extracts text from uploaded TXT, MD, PDF, or DOCX file."""
    file_extension = os.path.splitext(file_name)[1].lower()
    raw_text = ""
    try:
        if file_extension == ".txt" or file_extension == ".md":
            raw_text = file_bytes.decode()
        elif file_extension == ".pdf":
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                raw_text += page.extract_text() or ""
        elif file_extension == ".docx":
            doc = Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                raw_text += para.text + "\\n"
        else:
            st.error(
                f"Unsupported file type: {file_extension}. Please upload TXT, MD, PDF, or DOCX."
            )
            return None
    except Exception as e:
        st.error(f"Error processing file {file_name}: {e}")
        return None
    return raw_text


def format_resume_text_with_llm(raw_text, api_key):
    """Formats the extracted resume text using an LLM."""
    if not raw_text.strip():
        return ""
    try:
        llm = GoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            api_key=api_key,
        )
        template = """
        You are a text processing assistant.
        The following text was extracted from a resume file and might contain formatting errors,
        unnecessary characters, or be poorly structured.
        Please clean and reformat this text to be a clear, well-structured resume.
        Ensure that all key information (experience, education, skills, etc.) is preserved and presented logically.
        Remove any artifacts from the text extraction process. The output should be only the cleaned resume text.
        ---
        Raw Resume Text:
        ```
        {raw_resume_text}
        ```
        ---
        Cleaned and Formatted Resume Text:
        """
        prompt = PromptTemplate(
            input_variables=["raw_resume_text"],
            template=template,
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        formatted_text = chain.run(raw_resume_text=raw_text)
        print(f"Formatted resume text: {formatted_text}")
        return formatted_text.strip()

    except Exception as e:
        st.error(f"Error formatting resume text with LLM: {e}")
        return raw_text


def get_company_research(company_name: str, api_key: str) -> str:
    """
    Placeholder for company research agent.
    Currently, this function returns a placeholder message.
    A more advanced implementation would use web scraping tools or APIs
    to find and summarize information about the specified company.
    """

    return (
        f"Automated company research for '{company_name}' is a feature in development. "
        "This space would contain information gathered by the research agent. "
        "For now, please rely on the 'What else do you know about the company?' field for specific company insights."
    )


def main():
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    st.set_page_config(
        page_title="Hire Helper - AI Interview Prep",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            "Get Help": "https://github.com/tashifkhan/hirehelper",
            "Report a bug": "https://github.com/tashifkhan/hirehelper/issues",
            "About": "# Hire Helper\nYour AI-powered interview preparation companion!",
        },
    )

    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0

    if "text_to_copy" not in st.session_state:
        st.session_state.text_to_copy = ""
    if "show_copy_area" not in st.session_state:
        st.session_state.show_copy_area = False
    if "copied_question_num" not in st.session_state:
        st.session_state.copied_question_num = None
    if "copy_success" not in st.session_state:
        st.session_state.copy_success = {}

    st.markdown(
        """ 
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;400;500;600;700&display=swap');
    
    /* CSS Variables for consistent theming */
    :root {
        --primary-color: #0891B2;
        --primary-dark: #0E7490;
        --primary-light: #22D3EE;
        --secondary-color: #3B82F6;
        --secondary-light: #60A5FA;
        --accent-color: #06B6D4;
        --background-dark: #0F172A;
        --background-medium: #1E293B;
        --background-light: #334155;
        --background-card: #475569;
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --border-color: #64748B;
        --shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        --shadow-hover: 0 8px 24px rgba(8, 145, 178, 0.2);
        --border-radius: 12px;
        --border-radius-small: 8px;
        --gradient-primary: linear-gradient(135deg, #0891B2 0%, #22D3EE 50%, #3B82F6 100%);
        --gradient-secondary: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        --gradient-bg: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
    }

    /* Main app styling */
    .stApp {
        background: var(--gradient-bg);
        color: var(--text-primary);
        font-family: 'Comfortaa', -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 100vh;
        padding: 0 !important;
    }

    /* Main content container */
    .main .block-container {
        padding: 2rem 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }

    /* Center all main content */
    .main {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* Ensure proper spacing for content */
    .element-container {
        width: 100% !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* Center the title and subtitle */
    .element-container h1,
    .element-container .subtitle {
        text-align: center !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Responsive design */
    @media (max-width: 768px) {
        .stApp {
            padding-top: 1rem !important;
        }
        
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
        
        /* Mobile-friendly sidebar */
        .css-1d391kg {
            width: 100% !important;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .css-1d391kg.css-1aumxhk {
            transform: translateX(0);
        }
        
        /* Mobile title adjustments */
        h1 {
            font-size: 2rem !important;
            text-align: center;
            margin-bottom: 0.5rem !important;
        }
        
        /* Mobile button adjustments */
        .stButton > button {
            width: 100% !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Mobile input adjustments */
        .stTextInput input, .stTextArea textarea {
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--background-light) 0%, var(--background-medium) 100%);
        border-right: 3px solid var(--primary-color);
        box-shadow: var(--shadow);
        backdrop-filter: blur(10px);
        padding: 1.5rem 1rem !important;
    }

    .css-1d391kg .stMarkdown {
        color: var(--text-secondary);
    }

    /* Sidebar section headers */
    .css-1d391kg .stMarkdown h3 {
        color: var(--primary-color) !important;
        font-weight: 600 !important;
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid var(--primary-color) !important;
        font-size: 1.25rem !important;
    }

    /* Sidebar form elements spacing */
    .css-1d391kg .stTextInput,
    .css-1d391kg .stTextArea,
    .css-1d391kg .stNumberInput,
    .css-1d391kg .stFileUploader {
        margin-bottom: 1.5rem !important;
    }

    /* Sidebar button styling */
    .css-1d391kg .stButton {
        margin-bottom: 1rem !important;
    }

    /* Enhanced button styling */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: var(--border-radius-small);
        font-weight: 600;
        font-family: 'Comfortaa', sans-serif;
        padding: 0.875rem 1.75rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);
        text-transform: none;
        letter-spacing: 0.025em;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover {
        background: var(--gradient-secondary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Secondary button styling (remove buttons) */
    div[data-testid="column"] button {
        background: linear-gradient(135deg, #64748B 0%, #475569 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        font-weight: 500 !important;
        padding: 0.5rem !important;
        transition: all 0.3s ease !important;
        min-height: 2.5rem !important;
    }

    div[data-testid="column"] button:hover {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    }

    /* Modern input styling */
    .stTextInput input, 
    .stTextArea textarea, 
    .stNumberInput input {
        background-color: var(--background-card) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--border-radius-small) !important;
        color: var(--text-primary) !important;
        font-family: 'Comfortaa', sans-serif !important;
        font-size: 14px !important;
        padding: 0.875rem !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    .stTextInput input:focus, 
    .stTextArea textarea:focus, 
    .stNumberInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1), inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        outline: none !important;
        background-color: var(--background-light) !important;
    }

    .stTextArea textarea {
        min-height: 80px !important;
        resize: vertical !important;
    }

    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--border-radius) !important;
        background: linear-gradient(135deg, var(--background-card) 0%, var(--background-light) 100%) !important;
        padding: 2.5rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }

    .stFileUploader::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }

    .stFileUploader:hover::before {
        opacity: 0.05;
    }

    .stFileUploader:hover {
        border-color: var(--primary-color) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }

    .stFileUploader label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        position: relative;
        z-index: 1;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* File uploader content wrapper */
    .stFileUploader > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* File uploader section layout improvements */
    .stFileUploader section {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 1.5rem !important;
        width: 100% !important;
    }

    .stFileUploader section > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 1rem !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* File uploader text styling */
    .stFileUploader section p,
    .stFileUploader section span,
    .stFileUploader section small {
        text-align: center !important;
        display: block !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    /* Browse files button styling */
    .stFileUploader button {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        font-weight: 600 !important;
        font-family: 'Comfortaa', sans-serif !important;
        padding: 0.875rem 1.75rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3) !important;
        text-transform: none !important;
        letter-spacing: 0.025em !important;
        margin: 1rem auto 0 auto !important;
        position: relative !important;
        overflow: hidden !important;
        display: block !important;
        width: auto !important;
        min-width: 150px !important;
    }

    .stFileUploader button:hover {
        background: var(--gradient-secondary) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-hover) !important;
    }

    .stFileUploader button:active {
        transform: translateY(0) !important;
    }

    /* Hide ALL file uploader close/remove buttons - aggressive approach */
    .stFileUploader button[kind="secondary"],
    .stFileUploader button[data-testid="stButton"],
    .stFileUploader .stButton,
    .stFileUploader button:not([type="file"]):not(.stDownloadButton),
    .stFileUploader section button[title*="Remove"],
    .stFileUploader section button[title*="remove"],
    .stFileUploader section button[title*="Delete"],
    .stFileUploader section button[title*="delete"],
    .stFileUploader section button[title*="Clear"],
    .stFileUploader section button[title*="clear"],
    .stFileUploader section small + button,
    .stFileUploader div[data-testid="stFileUploaderDeleteBtn"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Hide any button that's not the main browse button */
    .stFileUploader section > div > button:not([type="button"]) {
        display: none !important;
    }

    /* Make sure only the browse files button is visible */
    .stFileUploader button[type="button"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Typography improvements */
    h1 {
        color: transparent !important;
        font-weight: 700 !important;
        font-size: 2.75rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    h2, h3 {
        color: var(--primary-color) !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        font-size: 1.5rem !important;
        line-height: 1.2 !important;
    }

    /* Special styling for sidebar headings */
    .css-1d391kg h3 {
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
        font-size: 1.25rem !important;
    }

    /* Section headers in main content */
    .element-container h2,
    .element-container h3 {
        text-align: left !important;
        padding-left: 0 !important;
    }

    .subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.125rem;
        margin-bottom: 2.5rem;
        font-weight: 400;
        line-height: 1.6;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Alert and notification styling */
    .stSuccess {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        padding: 1.25rem !important;
        box-shadow: var(--shadow) !important;
        border-left: 4px solid #34D399 !important;
    }

    .stWarning {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        padding: 1.25rem !important;
        box-shadow: var(--shadow) !important;
        border-left: 4px solid #FBBF24 !important;
    }

    .stError {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        padding: 1.25rem !important;
        box-shadow: var(--shadow) !important;
        border-left: 4px solid #F87171 !important;
    }

    .stInfo {
        background: var(--gradient-secondary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        padding: 1.25rem !important;
        box-shadow: var(--shadow) !important;
        border-left: 4px solid var(--secondary-light) !important;
    }

    /* Spinner styling */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
        border-right-color: var(--primary-light) !important;
    }

    /* Card-like containers for answers */
    .answer-card {
        background: linear-gradient(135deg, var(--background-card) 0%, var(--background-light) 100%);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--primary-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }

    .answer-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }

    .answer-card:hover::before {
        opacity: 0.02;
    }

    .answer-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-left-color: var(--accent-color);
    }

    .question-header {
        color: var(--primary-color);
        font-weight: 600;
        font-size: 1.125rem;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        position: relative;
        z-index: 1;
    }

    .answer-text {
        color: var(--text-primary);
        line-height: 1.7;
        font-size: 1rem;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }

    /* Horizontal dividers */
    hr {
        border: none !important;
        height: 2px !important;
        background: var(--gradient-primary) !important;
        margin: 3rem 0 !important;
        border-radius: 1px;
    }

    /* Copy area styling */
    .copy-area {
        background: linear-gradient(135deg, var(--background-card) 0%, var(--background-light) 100%);
        border: 2px solid var(--primary-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow);
    }

    .copy-area h4 {
        color: var(--primary-color) !important;
        margin-bottom: 0.75rem !important;
        font-size: 1.125rem !important;
    }

    /* Mobile-specific improvements */
    @media (max-width: 480px) {
        .stApp {
            padding: 0.75rem !important;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .subtitle {
            font-size: 1rem !important;
            margin-bottom: 2rem !important;
        }
        
        .answer-card {
            padding: 1.25rem !important;
            margin: 1rem 0 !important;
        }
        
        .stButton > button {
            padding: 0.75rem 1.25rem !important;
            font-size: 0.9rem !important;
        }
    }

    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* Focus indicators for better accessibility */
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px !important;
    }

    /* Column alignment improvements */
    div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
        gap: 0.5rem !important;
    }

    /* Question input sections */
    .css-1d391kg div[data-testid="column"] {
        gap: 0.75rem !important;
    }

    /* Question text areas specific styling */
    .css-1d391kg .stTextArea {
        margin-bottom: 1rem !important;
    }

    .css-1d391kg .stTextArea label {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
        font-size: 0.95rem !important;
    }

    /* Question remove button alignment */
    .css-1d391kg div[data-testid="column"]:last-child {
        justify-content: flex-end !important;
        padding-top: 1.5rem !important;
    }

    /* Form field container alignment */
    .stTextInput,
    .stTextArea,
    .stNumberInput,
    .stSelectbox {
        margin-bottom: 1rem !important;
    }

    /* Ensure labels are properly aligned */
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stSelectbox label {
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }

    /* Better button alignment in columns */
    div[data-testid="column"] .stButton {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: auto !important;
    }

    /* Remove button specific alignment */
    div[data-testid="column"] .stButton button {
        width: 100% !important;
        height: fit-content !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Progress bar styling */
    .stProgress > div > div {
        background: var(--gradient-primary) !important;
    }

    /* Expander styling */
    .streamlit-expander {
        background: var(--background-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius-small) !important;
        margin-bottom: 1.5rem !important;
    }

    .streamlit-expander:hover {
        border-color: var(--primary-color) !important;
    }

    /* Expander content alignment */
    .streamlit-expander .streamlit-expanderContent {
        padding: 1.5rem !important;
    }

    /* Expander header styling */
    .streamlit-expander .streamlit-expanderHeader {
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: var(--primary-color) !important;
        background: linear-gradient(135deg, var(--background-light) 0%, var(--background-card) 100%) !important;
        border-radius: var(--border-radius-small) var(--border-radius-small) 0 0 !important;
    }

    /* Better spacing within expanders */
    .streamlit-expanderContent .element-container {
        margin-bottom: 1rem !important;
    }

    /* Container spacing improvements */
    .element-container {
        margin-bottom: 1rem !important;
    }

    /* Better spacing for form sections */
    .stForm {
        border: none !important;
        padding: 0 !important;
    }

    /* Checkbox alignment */
    .stCheckbox {
        margin-bottom: 1.5rem !important;
    }

    .stCheckbox label {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }

    /* Copy button specific styling */
    .copy-button {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        min-width: 120px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
    }

    .copy-button:hover {
        background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }

    .copy-button-copied {
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%) !important;
        color: white !important;
    }

    /* Toast notification styling */
    .copy-toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius-small);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        font-family: 'Comfortaa', sans-serif;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1>Hire Helper</h1>", unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Your AI-powered interview preparation companion. Upload your resume, add questions, and get personalized answers that showcase your professional experience.</p>',
        unsafe_allow_html=True,
    )

    if not GOOGLE_API_KEY:
        st.error(
            "Please set the GOOGLE_API_KEY environment variable in your .env file to get started."
        )
        st.stop()

    is_mobile = st.checkbox(
        "Mobile view", value=False, help="Check this for better mobile experience"
    )

    if is_mobile:
        st.markdown("---")

        with st.expander("Configuration", expanded=True):
            uploaded_resume = st.file_uploader(
                "Upload Your Resume",
                type=["txt", "md", "pdf", "docx"],
                help="Supported formats: TXT, MD, PDF, DOCX",
                key=f"mobile_uploader_{st.session_state.file_uploader_key}",
            )

            # Add clear resume button for mobile
            if uploaded_resume:
                st.info(f"📄 **Uploaded:** {uploaded_resume.name}")
                if st.button(
                    "🗑️ Clear Resume",
                    key="clear_resume_mobile",
                    help="Remove the uploaded resume file",
                ):
                    # Clear the file uploader by incrementing the key
                    st.session_state.file_uploader_key += 1
                    st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            role = st.text_input(
                "Target Role", placeholder="e.g., Senior Software Engineer"
            )
            with col2:
                company = st.text_input(
                    "Target Company", placeholder="e.g., Innovatech Solutions"
                )

            user_additional_company_info_mobile = st.text_area(
                "What else do you know about the company?",
                placeholder="e.g., Their recent projects, company culture, specific challenges...",
                height=100,
                key="user_info_mobile",
            )

        with st.expander("Interview Questions", expanded=True):
            if "questions" not in st.session_state:
                st.session_state.questions = [""]

            def add_question_field():
                st.session_state.questions.append("")

            def remove_question_field(index):
                if len(st.session_state.questions) > 1:
                    st.session_state.questions.pop(index)
                else:
                    st.session_state.questions[index] = ""

            for i, q_text in enumerate(st.session_state.questions):
                cols = st.columns([0.85, 0.15])
                st.session_state.questions[i] = cols[0].text_area(
                    f"Question {i+1}",
                    value=q_text,
                    key=f"question_{i}",
                    height=80,
                    placeholder=f"Enter your interview question {i+1}...",
                )
                if len(st.session_state.questions) > 1:
                    cols[1].button(
                        "Remove",
                        key=f"remove_q_{i}",
                        on_click=remove_question_field,
                        args=(i,),
                        help="Remove this question",
                    )

            col1, col2 = st.columns([1, 1])
            with col1:
                st.button(
                    "Add Question",
                    on_click=add_question_field,
                    use_container_width=True,
                )
            with col2:
                word_limit = st.number_input(
                    "Word limit", min_value=20, max_value=500, value=100, step=10
                )

            generate_clicked = st.button(
                "Generate Answers", use_container_width=True, type="primary"
            )
    else:

        st.sidebar.markdown("### Configuration")
        uploaded_resume = st.sidebar.file_uploader(
            "Upload Your Resume",
            type=["txt", "md", "pdf", "docx"],
            help="Supported formats: TXT, MD, PDF, DOCX",
            key=f"desktop_uploader_{st.session_state.file_uploader_key}",
        )

        # Add clear resume button for desktop
        if uploaded_resume:
            st.sidebar.info(f"📄 **Uploaded:** {uploaded_resume.name}")
            if st.sidebar.button(
                "🗑️ Clear Resume",
                key="clear_resume_desktop",
                help="Remove the uploaded resume file",
            ):
                # Clear the file uploader by incrementing the key
                st.session_state.file_uploader_key += 1
                st.rerun()

        role = st.sidebar.text_input(
            "Target Role", placeholder="e.g., Senior Software Engineer"
        )
        company = st.sidebar.text_input(
            "Target Company", placeholder="e.g., Innovatech Solutions"
        )
        user_additional_company_info_desktop = st.sidebar.text_area(
            "What else do you know about the company?",
            placeholder="e.g., Their recent projects, company culture, specific challenges...",
            height=100,
            key="user_info_desktop",
        )

        st.sidebar.markdown("### Interview Questions")

        if "questions" not in st.session_state:
            st.session_state.questions = [""]

        def add_question_field():
            st.session_state.questions.append("")

        def remove_question_field(index):
            if len(st.session_state.questions) > 1:
                st.session_state.questions.pop(index)
            else:
                st.session_state.questions[index] = ""

        for i, q_text in enumerate(st.session_state.questions):
            cols = st.sidebar.columns([0.85, 0.15])
            st.session_state.questions[i] = cols[0].text_area(
                f"Question {i+1}",
                value=q_text,
                key=f"question_{i}",
                height=80,
                placeholder=f"Enter your interview question {i+1}...",
            )
            if len(st.session_state.questions) > 1:
                cols[1].button(
                    "×",
                    key=f"remove_q_{i}",
                    on_click=remove_question_field,
                    args=(i,),
                    help="Remove this question",
                )

        st.sidebar.button(
            "Add Question", on_click=add_question_field, use_container_width=True
        )

        word_limit = st.sidebar.number_input(
            "Word limit per answer",
            min_value=20,
            max_value=500,
            value=100,
            step=10,
            help="Maximum words per generated answer",
        )

        generate_clicked = st.sidebar.button(
            "Generate Answers", use_container_width=True, type="primary"
        )

    if is_mobile:
        user_additional_company_info = user_additional_company_info_mobile
    else:
        user_additional_company_info = user_additional_company_info_desktop

    if generate_clicked:
        if not uploaded_resume:
            st.warning("Please upload your resume to proceed.")
        elif not role.strip():
            st.warning("Please specify the target role.")
        elif not company.strip():
            st.warning("Please specify the target company.")
        elif not any(q.strip() for q in st.session_state.questions):
            st.warning("Please enter at least one interview question.")
        else:

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:

                status_text.text("Processing your resume...")
                progress_bar.progress(20)

                resume_bytes = uploaded_resume.read()
                raw_resume_text = process_document(resume_bytes, uploaded_resume.name)

                if not raw_resume_text:
                    st.stop()

                progress_bar.progress(40)
                resume_text = raw_resume_text
                file_extension = os.path.splitext(uploaded_resume.name)[1].lower()

                if file_extension in [".pdf", ".docx"]:
                    if raw_resume_text.strip():
                        status_text.text("AI is formatting your resume...")
                        progress_bar.progress(60)
                        resume_text = format_resume_text_with_llm(
                            raw_resume_text, GOOGLE_API_KEY
                        )
                        if not resume_text.strip():
                            st.warning(
                                "⚠️ Formatting resulted in empty resume text, using raw extracted text."
                            )
                            resume_text = raw_resume_text
                    else:
                        st.warning(
                            f"⚠️ No text could be extracted from {uploaded_resume.name}."
                        )
                        st.stop()

                if not resume_text.strip():
                    st.error(
                        "After processing, the resume text is empty. Cannot proceed."
                    )
                    st.stop()

                status_text.text(f"Researching {company}...")
                progress_bar.progress(70)
                company_research_data = ""
                if company.strip():
                    company_research_data = get_company_research(
                        company, GOOGLE_API_KEY
                    )

                if company_research_data and company.strip():
                    with st.expander(
                        f"Initial Research Findings for {company}", expanded=False
                    ):
                        st.markdown(company_research_data)

                status_text.text("✨ AI is crafting your personalized answers...")
                progress_bar.progress(90)

                valid_questions = [
                    q.strip() for q in st.session_state.questions if q.strip()
                ]
                if not valid_questions:
                    st.warning("❓ Please ensure at least one question is filled out.")
                    st.stop()

                answers = generate_answers(
                    resume_text,
                    role,
                    company,
                    valid_questions,
                    word_limit,
                    GOOGLE_API_KEY,
                    user_additional_company_info,
                    company_research_data,
                )

                progress_bar.progress(100)
                status_text.text("Complete!")

                progress_bar.empty()
                status_text.empty()

                if answers:
                    st.success("Your personalized interview answers are ready!")

                    for i, item in enumerate(answers, start=1):

                        st.markdown(
                            f"""<div class="answer-card">
                                <div class="question-header">
                                    <span>Question {i}</span>
                                </div>
                                <div style="color: var(--text-secondary); margin-bottom: 1rem; font-style: italic;">
                                    "{item['question']}"
                                </div>
                                <div class="answer-text">
                                    <strong>Your Answer:</strong><br>
                                    {item['answer']}
                                </div>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                        col1, col2, col3 = st.columns([3, 3, 2])

                        with col1:
                            if st.button(
                                f"📋 Show Copy Area Q{i}",
                                key=f"copy_q_{i}",
                                help="Click to show text area for copying",
                            ):
                                copy_area_key = f"show_copy_area_{i}"
                                if copy_area_key not in st.session_state:
                                    st.session_state[copy_area_key] = False
                                st.session_state[copy_area_key] = not st.session_state[
                                    copy_area_key
                                ]
                                st.rerun()

                        copy_area_key = f"show_copy_area_{i}"
                        if (
                            copy_area_key in st.session_state
                            and st.session_state[copy_area_key]
                        ):
                            st.markdown("---")
                            st.markdown(f"**📋 Copy Text for Question {i}:**")
                            st.info(
                                "💡 **Instructions:** Click in the text area below → Press Ctrl+A (Select All) → Press Ctrl+C (Copy)"
                            )

                            st.text_area(
                                f"Question {i} Answer (Ready to Copy):",
                                value=item["answer"],
                                height=150,
                                key=f"copy_text_area_{i}",
                                help="Click here, select all text (Ctrl+A), then copy (Ctrl+C)",
                                disabled=False,
                            )

                            col_close1, col_close2, col_close3 = st.columns([1, 2, 3])
                            with col_close1:
                                if st.button(f"❌ Hide", key=f"hide_copy_{i}"):
                                    st.session_state[copy_area_key] = False
                                    st.rerun()
                            with col_close2:
                                st.markdown("*Click Hide when done copying*")

                        st.markdown("---")
                else:
                    st.info("ℹ️ No questions were provided to generate answers for.")

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"An error occurred during answer generation: {e}")
                st.error("Please try again or check your inputs.")


if __name__ == "__main__":
    main()
