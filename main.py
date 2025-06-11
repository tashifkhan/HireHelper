import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


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
        "Upload Your Resume (TXT or MD)", type=["txt", "md"]
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
            st.session_state.questions[index] = ""  # Clear if only one question

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
            cols[1].empty()  # Keep layout consistent

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
                resume_text = resume_bytes.decode()

                # Filter out empty questions before passing to generate_answers
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
