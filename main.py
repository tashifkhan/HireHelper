import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


def generate_answers(resume_text, role, company, questions_str, word_limit, api_key):
    """Generates answers to interview questions based on the resume and inputs."""
    questions = [q.strip() for q in questions_str.split(";") if q.strip()]
    if not questions:
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
    for q in questions:
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
        page_title="Interview Helper",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Interview Preparation Assistant")
    st.markdown("Prepare for your interview with AI-generated answers.")

    if not GOOGLE_API_KEY:
        st.error(
            "Please set the GOOGLE_API_KEY environment variable in your .env file."
        )
        st.stop()

    # --- Sidebar for Inputs ---
    st.sidebar.header("Job Details")
    uploaded_resume = st.sidebar.file_uploader(
        "Upload your Resume (TXT or MD)", type=["txt", "md"]
    )

    role = st.sidebar.text_input(
        "Role you’re applying for:", placeholder="e.g., Software Engineer"
    )
    company = st.sidebar.text_input(
        "Company name:", placeholder="e.g., Tech Solutions Inc."
    )

    st.sidebar.header("Interview Questions")
    raw_qs = st.sidebar.text_area(
        "Enter interview questions, separated by ';'",
        placeholder="e.g., Tell me about yourself; Why are you interested in this role?",
        height=150,
    )
    word_limit = st.sidebar.number_input(
        "Word limit per answer:", min_value=20, max_value=500, value=100, step=10
    )

    if st.sidebar.button("Generate Answers", use_container_width=True):
        if not uploaded_resume:
            st.warning("Please upload your resume.")
        elif not role:
            st.warning("Please enter the role you are applying for.")
        elif not company:
            st.warning("Please enter the company name.")
        elif not raw_qs:
            st.warning("Please enter the interview questions.")
        else:
            try:
                resume_bytes = uploaded_resume.read()
                resume_text = resume_bytes.decode()

                with st.spinner("Generating answers... Please wait..."):
                    answers = generate_answers(
                        resume_text, role, company, raw_qs, word_limit, GOOGLE_API_KEY
                    )

                if answers:
                    st.success("Answers generated successfully:")
                    for i, item in enumerate(answers, start=1):
                        st.subheader(f"Q{i}: {item['question']}")
                        st.markdown(f"A{i}: {item['answer']}")
                        st.markdown("---")
                else:
                    st.info("No questions were provided to answer.")
            except Exception as e:
                st.error(f"An error occurred: {e}")


main()
