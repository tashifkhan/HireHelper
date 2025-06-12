import os
import io
import json
from langchain_google_genai import GoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from PyPDF2 import PdfReader
from docx import Document
import streamlit as st


def generate_answers(
    resume_text,
    role,
    company,
    questions_list,
    word_limit,
    model_provider,
    model_name,
    api_keys_dict,
    user_company_knowledge="",
    company_research="",
):
    """Generates answers to interview questions based on the resume and inputs."""
    if not questions_list:
        return []

    llm = None
    try:
        if model_provider == "Google":
            if not api_keys_dict.get("Google"):
                raise ValueError("Google API Key not provided.")
            llm = GoogleGenerativeAI(
                model=model_name,
                temperature=0.3,
                google_api_key=api_keys_dict["Google"],
            )
        elif model_provider == "OpenAI":
            if not api_keys_dict.get("OpenAI"):
                raise ValueError("OpenAI API Key not provided.")
            llm = ChatOpenAI(
                model_name=model_name,
                temperature=0.3,
                openai_api_key=api_keys_dict["OpenAI"],
            )
        elif model_provider == "Claude":
            if not api_keys_dict.get("Claude"):
                raise ValueError("Anthropic API Key not provided.")
            llm = ChatAnthropic(
                model=model_name,
                temperature=0.3,
                anthropic_api_key=api_keys_dict["Claude"],
            )
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")

    except ValueError as ve:
        error_msg = str(ve)
        provider_help = {
            "Google": "Verify your Google API key at https://aistudio.google.com/app/apikey",
            "OpenAI": "Verify your OpenAI API key at https://platform.openai.com/api-keys",
            "Claude": "Verify your Anthropic API key at https://console.anthropic.com/",
        }

        for provider, help_text in provider_help.items():
            if provider in error_msg:
                error_msg += f"\n💡 {help_text}"
                break

        return [
            {"question": q, "answer": f"Configuration Error: {error_msg}"}
            for q in questions_list
        ]
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if "rate limit" in str(e).lower():
            error_msg += (
                "\n💡 You may have hit API rate limits. Try again in a few moments."
            )
        elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            error_msg += (
                "\n💡 Please check your API key is valid and has sufficient credits."
            )
        elif "connection" in str(e).lower() or "network" in str(e).lower():
            error_msg += (
                "\n💡 Network connection issue. Please check your internet connection."
            )

        return [
            {"question": q, "answer": f"Error: {error_msg}"} for q in questions_list
        ]

    # Build context about the company
    company_context = ""
    if user_company_knowledge.strip():
        company_context += f"\n\nAdditional information about {company}:\n{user_company_knowledge.strip()}"
    if company_research.strip():
        company_context += (
            f"\n\nResearch findings about {company}:\n{company_research.strip()}"
        )

    template = """
    You are an expert interview coach and career advisor.

    Below is the candidate’s résumé (Markdown):
    ```
    {resume}
    ```

    They are applying for the role of **{role}** at **{company}**{company_context}.

    Your task: craft a clear, concise answer (≤ {word_limit} words) to the interview question below.

    Question:
    {question}

    Formatting guidelines:
    1. Start with a one-sentence summary of why this candidate is a great fit.
    2. Then use 3–4 bullet points that each:
    • Reference a specific skill or achievement from the résumé  
    • Include metrics or outcomes whenever possible  
    • Tie back to the company’s mission, values or culture  
    3. Maintain a professional, confident tone.
    4. If no {company_context} is provided, skip references to company culture.

    Answer:
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
                raw_text += para.text + "\n"
        else:
            st.error(
                f"Unsupported file type: {file_extension}. Please upload TXT, MD, PDF, or DOCX."
            )
            return None
    except Exception as e:
        st.error(f"Error processing file {file_name}: {e}")
        return None
    return raw_text


def format_resume_text_with_llm(raw_text, model_provider, model_name, api_keys_dict):
    """Formats the extracted resume text using an LLM."""
    if not raw_text.strip():
        return ""
    llm = None
    try:
        if model_provider == "Google":
            if not api_keys_dict.get("Google"):
                raise ValueError("Google API Key not provided for resume formatting.")
            llm = GoogleGenerativeAI(
                model=model_name,
                temperature=0.1,
                google_api_key=api_keys_dict["Google"],
            )
        elif model_provider == "OpenAI":
            if not api_keys_dict.get("OpenAI"):
                raise ValueError("OpenAI API Key not provided for resume formatting.")
            llm = ChatOpenAI(
                model_name=model_name,
                temperature=0.1,
                openai_api_key=api_keys_dict["OpenAI"],
            )
        elif model_provider == "Claude":
            if not api_keys_dict.get("Claude"):
                raise ValueError(
                    "Anthropic API Key not provided for resume formatting."
                )
            llm = ChatAnthropic(
                model=model_name,
                temperature=0.1,
                anthropic_api_key=api_keys_dict["Claude"],
            )
        else:
            raise ValueError(
                f"Unsupported model provider for resume formatting: {model_provider}"
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

    except ValueError as ve:
        error_msg = str(ve)
        provider_help = {
            "Google": "Verify your Google API key at https://aistudio.google.com/app/apikey",
            "OpenAI": "Verify your OpenAI API key at https://platform.openai.com/api-keys",
            "Claude": "Verify your Anthropic API key at https://console.anthropic.com/",
        }

        for provider, help_text in provider_help.items():
            if provider in error_msg:
                st.error(f"Resume formatting failed: {error_msg}\n💡 {help_text}")
                break
        else:
            st.error(f"Resume formatting failed: {error_msg}")

        return raw_text  # Return original text on specific API key errors
    except Exception as e:
        error_msg = f"Error formatting resume text: {str(e)}"
        if "rate limit" in str(e).lower():
            error_msg += "\n💡 You may have hit API rate limits. Using original text."
        elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            error_msg += "\n💡 API authentication issue. Using original text."

        st.warning(error_msg)
        return raw_text  # Return original text on other errors


def estimate_cost(provider, model_name, resume_length, num_questions, word_limit):
    """Estimate the cost of using different providers."""

    # Rough token estimates (1 token ≈ 0.75 words)
    resume_tokens = resume_length // 4 * 5  # Resume tokens (input)
    question_tokens = num_questions * 50  # Question tokens (input)
    answer_tokens = num_questions * word_limit * 1.3  # Answer tokens (output)

    total_input_tokens = resume_tokens + question_tokens
    total_output_tokens = answer_tokens

    # Pricing per 1M tokens (approximate, as of 2025)
    pricing = {
        "Google": {
            "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
            "gemini-1.5-pro-latest": {"input": 3.50, "output": 10.50},
            "gemini-1.5-pro": {"input": 3.50, "output": 10.50},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15},
        },
        "OpenAI": {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        },
        "Claude": {
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku-20241022": {"input": 0.25, "output": 1.25},
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        },
    }

    if provider not in pricing or model_name not in pricing[provider]:
        return "Cost estimation not available"

    model_pricing = pricing[provider][model_name]

    input_cost = (total_input_tokens / 1000000) * model_pricing["input"]
    output_cost = (total_output_tokens / 1000000) * model_pricing["output"]
    total_cost = input_cost + output_cost

    if total_cost < 0.01:
        return "< $0.01"
    else:
        return f"~${total_cost:.3f}"


def test_api_key(provider, api_key, model_name):
    """Test if an API key is valid by making a small test request."""
    if not api_key:
        return False, "No API key provided"

    try:
        test_prompt = "Hello"

        if provider == "Google":
            llm = GoogleGenerativeAI(
                model=model_name,
                temperature=0.1,
                google_api_key=api_key,
            )
        elif provider == "OpenAI":
            llm = ChatOpenAI(
                model_name=model_name,
                temperature=0.1,
                openai_api_key=api_key,
                max_tokens=10,
            )
        elif provider == "Claude":
            llm = ChatAnthropic(
                model=model_name,
                temperature=0.1,
                anthropic_api_key=api_key,
                max_tokens=10,
            )
        else:
            return False, f"Unsupported provider: {provider}"

        # Make a minimal test call
        response = llm.invoke(test_prompt)
        return True, "API key is valid"

    except Exception as e:
        error_msg = str(e).lower()
        if "authentication" in error_msg or "unauthorized" in error_msg:
            return False, "Invalid API key"
        elif "rate limit" in error_msg:
            return False, "Rate limited (but key is likely valid)"
        elif "model" in error_msg:
            return False, f"Model '{model_name}' not available"
        else:
            return False, f"Connection error: {str(e)[:100]}"


def get_company_research(company_name: str, api_keys_dict: dict) -> str:
    """Gets basic company research information."""
    # This is a placeholder function for company research
    # In a real implementation, this would scrape company websites,
    # news articles, or use APIs to gather company information
    return f"Research about {company_name}: This is a placeholder for company research functionality."


# Model descriptions for UI
model_descriptions = {
    "gemini-2.0-flash-exp": "Latest experimental - fastest & most capable",
    "gemini-1.5-pro-latest": "Production-ready - best balance",
    "gemini-1.5-pro": "Stable pro - complex reasoning",
    "gemini-1.5-flash": "Fast - good for quick tasks",
    "gemini-1.5-flash-8b": "Smallest - ultra fast",
    "gpt-4o": "Latest GPT-4 - most capable",
    "gpt-4o-mini": "Smaller GPT-4 - good value",
    "gpt-4-turbo": "Fast GPT-4 - optimized speed",
    "gpt-4": "Original GPT-4 - reliable",
    "gpt-3.5-turbo": "Budget option - fast & cheap",
    "claude-3-5-sonnet-20241022": "Best Claude - excellent reasoning",
    "claude-3-5-haiku-20241022": "Fast Claude - quick responses",
    "claude-3-opus-20240229": "Most capable Claude - complex tasks",
    "claude-3-sonnet-20240229": "Balanced Claude - all-rounder",
    "claude-3-haiku-20240307": "Fastest Claude - simple tasks",
}

# Model options for different providers
model_options = {
    "Google": [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ],
    "Claude": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
}
