import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.document_loaders import TextLoader


def main():

    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

    loader = TextLoader("resume.md")
    doc = loader.load()[0]
    resume_text = doc.page_content

    role = input("Role you’re applying for: ").strip()
    company = input("Company name: ").strip()
    raw_qs = input("Enter interview questions, separated by ';':\n").strip()
    word_limit = input("Word limit per answer: ").strip()

    questions = [q.strip() for q in raw_qs.split(";") if q.strip()]

    llm = GoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        api_key=GOOGLE_API_KEY,
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

    for i, q in enumerate(questions, start=1):
        answer = chain.run(
            resume=resume_text,
            role=role,
            company=company,
            question=q,
            word_limit=word_limit,
        )
        print(f"\nQ{i}: {q}\nA{i}: {answer}\n{'-'*40}")


if __name__ == "__main__":
    main()
