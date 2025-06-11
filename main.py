import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import io  # Added for BytesIO
from PyPDF2 import PdfReader  # Added for PDF processing
from docx import Document  # Added for DOCX processing


def generate_answers(resume_text, role, company, questions_list, word_limit, api_key):
    """Generates answers to interview questions based on the resume and inputs."""
    if not questions_list:
        return []

    llm = GoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        api_key=api_key,
    )

    template = """
    You are an expert interview coach.
    A candidate with this résumé:
    ```
    {resume}
    ```
    is applying for the role of {role} at {company}.
    Answer the question below in at most {word_limit} words,
    drawing on experiences and skills from the résumé.
    ---
    Question: {question}
    """

    prompt = PromptTemplate(
        input_variables=["resume", "role", "company", "question", "word_limit"],
        template=template,
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    results = []
    for q in questions_list:  # Iterate over the provided list
        try:
            answer = chain.run(
                resume=resume_text,
                role=role,
                company=company,
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
            model="gemini-2.0-flash",  # Using gemini-2.0-flash as a light model
            temperature=0.1,  # Low temperature for more deterministic formatting
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
        return formatted_text.strip()
    except Exception as e:
        st.error(f"Error formatting resume text with LLM: {e}")
        return raw_text  # Fallback to raw text if formatting fails


def main():
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    st.set_page_config(
        page_title="Interview Spark - AI Prep Assistant",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for dark theme with deeper orange accents
    st.markdown(
        """ 
    <style>
    /* Main app background */
    .stApp {
        background-color: #1A1A1A; /* Darker background */
        color: #F0F0F0; /* Lighter text */
    }

    /* Sidebar styling */
    .css-1d391kg { /* Sidebar main */
        background-color: #262626; /* Slightly lighter dark for sidebar */
        border-right: 1px solid #FF8C00; /* Deeper orange sidebar border */
    }
    .css-1d391kg .st-emotion-cache-10oheav { /* Sidebar header */
        color: #FF8C00; /* Deeper orange accent for sidebar headers */
        border-bottom: 1px solid #444444;
        padding-bottom: 0.5rem;
    }

    /* Button styling */
    .stButton>button {
        background-color: #FF8C00; /* Fallback background color */
        background-image: linear-gradient(to right, #FF8C00 0%, #FFA500 50%, #FF8C00 100%); /* Orange gradient */
        color: #1A1A1A; /* Dark text for buttons */
        border-radius: 6px;
        border: 1px solid #E07B00; /* Slightly darker orange border */
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #E07B00; /* Fallback background color */
        background-image: linear-gradient(to right, #E07B00 0%, #FF8C00 50%, #E07B00 100%); /* Darker orange gradient on hover */
        color: #FFFFFF;
        border: 1px solid #FFAD33; /* Lighter orange border on hover for contrast */
    }

    /* Specific styling for Remove Question button */
    div[data-testid="column"] button {
        background-color: #4A4A4A !important; /* Darker grey for remove button */
        color: #D0D0D0 !important; /* Lighter text */
        border: 1px solid #333333 !important;
        background-image: none !important; /* Remove gradient for this specific button */
    }
    div[data-testid="column"] button:hover {
        background-color: #5A5A5A !important;
        color: #FFFFFF !important;
        border: 1px solid #FF8C00 !important;
    }

    /* Input fields styling */
    .stTextInput input, 
    .stTextArea textarea, 
    .stNumberInput input {
        border: 2px solid #FF8C00 !important; /* Deeper orange, thicker border */
        background-color: #2A2A2A !important; 
        color: #F0F0F0 !important; 
        border-radius: 6px !important; /* Slightly more rounded corners */
        padding: 0.5em !important; /* Add some padding inside the input */
    }

    .stTextArea textarea {
        resize: vertical; /* Allow vertical resize, disable horizontal if not desired */
    }

    .stFileUploader label { /* Specific styling for file uploader label */
        border-radius: 6px;
        padding: 8px;
        border: 2px dashed #FF8C00 !important; /* Dashed border for drop zone, thicker */
        background-color: #2A2A2A !important;
    }
    .stFileUploader label:hover {
        border-color: #E07B00 !important;
        background-color: #303030 !important;
    }


    /* Titles and Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #FF8C00; /* Deeper orange for titles */
    }
    .st-emotion-cache-10trblm { /* Main title */
        color: #FF8C00; /* Deeper orange for main title */
        border-bottom: 2px solid #FF8C00;
        padding-bottom: 0.3em;
    }
    .stMarkdown p { /* Main markdown text */
        color: #D0D0D0; /* Lighter grey for paragraph text */
    }
    .stSuccess { /* Success box */
        background-color: #1F3A24 !important; /* Darker green for success */
        color: #A3D9A5 !important; /* Softer green text */
        border: 1px solid #FF8C00 !important;
        border-left: 5px solid #FF8C00 !important;
        border-radius: 4px;
    }
    .stWarning { /* Warning box */
        background-color: #4A3220 !important; /* Darker orange for warning */
        color: #FFD79A !important; /* Softer gold text */
        border: 1px solid #FF8C00 !important;
        border-left: 5px solid #FF8C00 !important;
        border-radius: 4px;
    }
    .stError { /* Error box */
        background-color: #4C2525 !important; /* Darker red for error */
        color: #FFA0A0 !important; /* Softer pink text */
        border: 1px solid #FF8C00 !important;
        border-left: 5px solid #FF8C00 !important;
        border-radius: 4px;
    }
    .stInfo { /* Info box */
      background-color: #20303F !important; /* Darker blue for info */
      color: #A0C8E0 !important; /* Softer blue text */
      border: 1px solid #FF8C00 !important;
      border-left: 5px solid #FF8C00 !important;
      border-radius: 4px;
    }

    /* Horizontal rule */
    hr {
        border-top: 1px solid #FF8C00; /* Deeper orange horizontal rule */
    }

    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("Hire Helper: AI Prep Co-Pilot")
    st.markdown("Ignite your success. Let's craft winning answers together.")

    if not GOOGLE_API_KEY:
        st.error(
            "Please set the GOOGLE_API_KEY environment variable in your .env file."
        )
        st.stop()

    # --- Sidebar for Inputs ---
    st.sidebar.header("Configure Your Session")
    uploaded_resume = st.sidebar.file_uploader(
        "Upload Your Resume (TXT, MD, PDF, DOCX)",
        type=["txt", "md", "pdf", "docx"],
    )

    role = st.sidebar.text_input(
        "Target Role:", placeholder="e.g., Senior Software Engineer"
    )
    company = st.sidebar.text_input(
        "Target Company:", placeholder="e.g., Innovatech Solutions"
    )

    st.sidebar.header("Interview Intel")

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
        st.session_state.questions[i] = cols[0].text_input(
            f"Question {i+1}",
            value=q_text,
            key=f"question_{i}",
            label_visibility="collapsed",
            placeholder=f"Enter question {i+1}",
        )
        if len(st.session_state.questions) > 1:
            cols[1].button(
                "-",
                key=f"remove_q_{i}",
                on_click=remove_question_field,
                args=(i,),
                use_container_width=True,
            )
        else:
            cols[1].empty()

    st.sidebar.button(
        "Add Question", on_click=add_question_field, use_container_width=True
    )

    word_limit = st.sidebar.number_input(
        "Word limit per answer:", min_value=20, max_value=500, value=100, step=10
    )

    if st.sidebar.button("Generate Answers", use_container_width=True):
        if not uploaded_resume:
            st.warning("Please upload your resume to proceed.")
        elif not role:
            st.warning("Please specify the target role.")
        elif not company:
            st.warning("Please specify the target company.")
        elif not any(q.strip() for q in st.session_state.questions):
            st.warning("Please enter at least one interview question.")
        else:
            try:
                resume_bytes = uploaded_resume.read()
                raw_resume_text = process_document(resume_bytes, uploaded_resume.name)

                if not raw_resume_text:
                    st.stop()

                resume_text = raw_resume_text
                file_extension = os.path.splitext(uploaded_resume.name)[1].lower()

                if file_extension in [".pdf", ".docx"]:
                    if raw_resume_text.strip():
                        with st.spinner(
                            "AI is formatting your resume... Please wait..."
                        ):
                            resume_text = format_resume_text_with_llm(
                                raw_resume_text, GOOGLE_API_KEY
                            )
                        if not resume_text.strip():
                            st.warning(
                                "Formatting resulted in empty resume text, using raw extracted text."
                            )
                            resume_text = raw_resume_text
                    else:
                        st.warning(
                            f"No text could be extracted from {uploaded_resume.name}."
                        )
                        st.stop()

                if not resume_text.strip():
                    st.error(
                        "After processing, the resume text is empty. Cannot proceed."
                    )
                    st.stop()

                valid_questions = [
                    q.strip() for q in st.session_state.questions if q.strip()
                ]
                if not valid_questions:
                    st.warning("Please ensure at least one question is filled out.")
                    st.stop()

                with st.spinner("AI is crafting your answers... Please wait..."):
                    answers = generate_answers(
                        resume_text,
                        role,
                        company,
                        valid_questions,
                        word_limit,
                        GOOGLE_API_KEY,
                    )

                if answers:
                    st.success("Answers generated successfully:")
                    for i, item in enumerate(answers, start=1):
                        st.subheader(f"Q{i}: {item['question']}")
                        st.markdown(
                            f"<div style='background-color: #2A2A2A; padding: 12px; border-left: 5px solid #FF8C00; margin-bottom: 12px; border-radius: 4px; border: 1px solid #444444;'>A{i}: {item['answer']}</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown("---")
                else:
                    st.info("No questions were provided to generate answers for.")
            except Exception as e:
                st.error(f"An error occurred during answer generation: {e}")


main()
