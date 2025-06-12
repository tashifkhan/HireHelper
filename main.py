import os
import json
import streamlit as st
from dotenv import load_dotenv
from streamlit.components.v1 import html

# Import all business logic from utils
from utils import (
    svg_icons,
    generate_answers,
    process_document,
    format_resume_text_with_llm,
    estimate_cost,
    test_api_key,
    get_company_research,
    model_descriptions,
    model_options,
)


def main():
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    st.set_page_config(
        page_title="Hire Helper - AI Interview Prep",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            "Get Help": "https://github.com/tashifkhan/hirehelper",
            "Report a bug": "https://github.com/tashifkhan/hirehelper/issues",
            "About": "# Hire Helper\\nYour AI-powered interview preparation companion!",
        },
    )

    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0

    if "questions" not in st.session_state:
        st.session_state.questions = [""]

    # Initialize API keys in session state
    if "saved_api_keys" not in st.session_state:
        st.session_state.saved_api_keys = {"Google": "", "OpenAI": "", "Claude": ""}

    st.markdown(
        """ 
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* CSS Variables for consistent theming */
    :root {
        --primary-color: #6366F1;
        --primary-dark: #4F46E5;
        --primary-light: #818CF8;
        --secondary-color: #8B5CF6;
        --secondary-light: #A78BFA;
        --accent-color: #06B6D4;
        --accent-warm: #F59E0B;
        --background-primary: #0F0F23;
        --background-secondary: #1A1A40;
        --background-tertiary: #262654;
        --background-card: #2D2D5F;
        --background-surface: #3A3A6B;
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --text-accent: #A5B4FC;
        --border-color: #4B5563;
        --border-light: #6B7280;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        --shadow-hover: 0 12px 40px rgba(99, 102, 241, 0.25);
        --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);
        --border-radius: 16px;
        --border-radius-small: 12px;
        --border-radius-large: 24px;
        --gradient-primary: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #06B6D4 100%);
        --gradient-secondary: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
        --gradient-accent: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%);
        --gradient-warm: linear-gradient(135deg, #F59E0B 0%, #EF4444 100%);
        --gradient-bg: linear-gradient(135deg, #0F0F23 0%, #1A1A40 50%, #262654 100%);
        --gradient-surface: linear-gradient(135deg, rgba(45, 45, 95, 0.8) 0%, rgba(58, 58, 107, 0.8) 100%);
        --glass-bg: rgba(45, 45, 95, 0.1);
        --glass-border: rgba(139, 92, 246, 0.2);
        --backdrop-blur: blur(20px);
        --transition-fast: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-bounce: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    /* Animated background patterns */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(6, 182, 212, 0.05) 0%, transparent 50%);
        animation: backgroundShift 20s ease-in-out infinite alternate;
        pointer-events: none;
        z-index: -1;
    }

    @keyframes backgroundShift {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(20px, -20px) rotate(1deg); }
    }

    /* Floating particles */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(255, 255, 255, 0.1), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(99, 102, 241, 0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(139, 92, 246, 0.15), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(6, 182, 212, 0.1), transparent);
        background-repeat: repeat;
        background-size: 200px 150px;
        animation: particleFloat 25s linear infinite;
        pointer-events: none;
        z-index: -1;
        opacity: 0.6;
    }

    @keyframes particleFloat {
        0% { transform: translateY(0px); }
        100% { transform: translateY(-100vh); }
    }

    /* Main app styling */
    .stApp {
        background: var(--gradient-bg);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 100vh;
        padding: 0 !important;
        position: relative;
        overflow-x: hidden;
    }

    /* Main content container */
    .main .block-container {
        padding: 2rem 1rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
        width: 100% !important;
        position: relative;
        z-index: 1;
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
        max-width: 1400px !important;
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

    /* Advanced Sidebar styling with glassmorphism */
    .css-1d391kg {
        background: var(--glass-bg) !important;
        backdrop-filter: var(--backdrop-blur) !important;
        -webkit-backdrop-filter: var(--backdrop-blur) !important;
        border-right: 3px solid var(--glass-border) !important;
        box-shadow: 
            var(--shadow),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        padding: 2rem 1.5rem !important;
        position: relative;
        overflow: hidden;
    }

    /* Sidebar glow effect */
    .css-1d391kg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
            45deg,
            rgba(99, 102, 241, 0.05) 0%,
            rgba(139, 92, 246, 0.05) 50%,
            rgba(6, 182, 212, 0.05) 100%
        );
        pointer-events: none;
        z-index: -1;
    }

    .css-1d391kg .stMarkdown {
        color: var(--text-secondary);
    }

    /* Modern sidebar section headers */
    .css-1d391kg .stMarkdown h3 {
        color: var(--primary-light) !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        margin-top: 0 !important;
        margin-bottom: 2rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 2px solid var(--primary-color) !important;
        position: relative;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .css-1d391kg .stMarkdown h3::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: var(--gradient-primary);
        border-radius: 2px;
    }

    /* Sidebar form elements spacing */
    .css-1d391kg .stTextInput,
    .css-1d391kg .stTextArea,
    .css-1d391kg .stNumberInput,
    .css-1d391kg .stFileUploader,
    .css-1d391kg .stSelectbox {
        margin-bottom: 2rem !important;
    }

    /* Advanced button styling with 3D effects */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: var(--border-radius-small);
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        padding: 1rem 2rem;
        transition: var(--transition-smooth);
        box-shadow: 
            0 8px 25px rgba(99, 102, 241, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        text-transform: none;
        letter-spacing: 0.025em;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        transform: translateY(0);
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover {
        background: var(--gradient-secondary);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 
            var(--shadow-hover),
            var(--shadow-glow),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(1.01);
        transition: var(--transition-fast);
    }

    /* Remove button styling */
    div[data-testid="column"] button {
        background: linear-gradient(135deg, var(--background-surface) 0%, var(--background-card) 100%) !important;
        color: var(--text-secondary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--border-radius-small) !important;
        font-weight: 500 !important;
        padding: 0.75rem !important;
        transition: var(--transition-smooth) !important;
        min-height: 3rem !important;
        backdrop-filter: blur(10px) !important;
    }

    div[data-testid="column"] button:hover {
        background: var(--gradient-warm) !important;
        color: white !important;
        border-color: var(--accent-warm) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3) !important;
    }

    /* Advanced input styling with floating labels effect */
    .stTextInput input, 
    .stTextArea textarea, 
    .stNumberInput input,
    .stSelectbox > div > div {
        background: var(--glass-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--border-radius-small) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 1rem 1.25rem !important;
        transition: var(--transition-smooth) !important;
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.1),
            0 0 0 0 rgba(99, 102, 241, 0) !important;
        backdrop-filter: blur(10px) !important;
        position: relative;
    }

    .stTextInput input:focus, 
    .stTextArea textarea:focus, 
    .stNumberInput input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 
            0 0 0 4px rgba(99, 102, 241, 0.1),
            inset 0 2px 4px rgba(0, 0, 0, 0.1),
            var(--shadow-glow) !important;
        outline: none !important;
        background: var(--background-surface) !important;
        transform: translateY(-2px);
    }

    .stTextArea textarea {
        min-height: 100px !important;
        resize: vertical !important;
    }

    /* Advanced File uploader with animated upload zone */
    .stFileUploader {
        border: 3px dashed var(--border-light) !important;
        border-radius: var(--border-radius-large) !important;
        background: var(--glass-bg) !important;
        backdrop-filter: var(--backdrop-blur) !important;
        padding: 3rem !important;
        text-align: center !important;
        transition: var(--transition-bounce) !important;
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
        transition: var(--transition-smooth);
        pointer-events: none;
    }

    .stFileUploader::after {
        content: '⬆';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 4rem;
        opacity: 0.1;
        pointer-events: none;
        transition: var(--transition-smooth);
    }

    .stFileUploader:hover::before {
        opacity: 0.05;
    }

    .stFileUploader:hover::after {
        opacity: 0.3;
        transform: translate(-50%, -50%) scale(1.1);
    }

    .stFileUploader:hover {
        border-color: var(--primary-color) !important;
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--shadow-hover);
        background: var(--background-surface) !important;
    }

    /* Advanced typography with text effects */
    h1 {
        color: transparent !important;
        font-weight: 800 !important;
        font-size: 3.5rem !important;
        margin-bottom: 1rem !important;
        text-align: center;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        position: relative;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    h1::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 120px;
        height: 4px;
        background: var(--gradient-primary);
        border-radius: 2px;
        animation: titleGlow 2s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
        0% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.5); }
        100% { box-shadow: 0 0 40px rgba(139, 92, 246, 0.8); }
    }

    h2, h3 {
        color: var(--primary-light) !important;
        font-weight: 700 !important;
        margin-top: 3rem !important;
        margin-bottom: 2rem !important;
        font-size: 1.8rem !important;
        line-height: 1.2 !important;
        position: relative;
    }

    .subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.25rem;
        margin-bottom: 3rem;
        font-weight: 400;
        line-height: 1.6;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        opacity: 0.9;
    }

    /* Advanced alert styling with icons */
    .stSuccess {
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 1.5rem !important;
        box-shadow: 
            var(--shadow),
            0 0 30px rgba(16, 185, 129, 0.2) !important;
        border-left: 5px solid #34D399 !important;
        backdrop-filter: blur(10px) !important;
        position: relative;
        overflow: hidden;
    }

    .stWarning {
        background: linear-gradient(135deg, var(--warning) 0%, #D97706 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 1.5rem !important;
        box-shadow: 
            var(--shadow),
            0 0 30px rgba(245, 158, 11, 0.2) !important;
        border-left: 5px solid #FBBF24 !important;
        backdrop-filter: blur(10px) !important;
    }

    .stError {
        background: linear-gradient(135deg, var(--error) 0%, #DC2626 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 1.5rem !important;
        box-shadow: 
            var(--shadow),
            0 0 30px rgba(239, 68, 68, 0.2) !important;
        border-left: 5px solid #F87171 !important;
        backdrop-filter: blur(10px) !important;
    }

    .stInfo {
        background: var(--gradient-secondary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 1.5rem !important;
        box-shadow: 
            var(--shadow),
            0 0 30px rgba(139, 92, 246, 0.2) !important;
        border-left: 5px solid var(--secondary-light) !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Advanced loading spinner */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
        border-right-color: var(--primary-light) !important;
        animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite !important;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Advanced answer cards with 3D effects */
    .answer-card {
        background: var(--glass-bg);
        backdrop-filter: var(--backdrop-blur);
        border: 2px solid var(--glass-border);
        border-left: 6px solid var(--primary-color);
        border-radius: var(--border-radius-large);
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 
            var(--shadow),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: var(--transition-smooth);
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
        transition: var(--transition-smooth);
        pointer-events: none;
    }

    .answer-card:hover::before {
        opacity: 0.03;
    }

    .answer-card:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 
            var(--shadow-hover),
            var(--shadow-glow),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-left-color: var(--accent-color);
        border-color: var(--primary-light);
    }

    .question-header {
        color: var(--primary-light);
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        position: relative;
        z-index: 1;
    }

    .question-header::before {
        content: '';
        width: 8px;
        height: 8px;
        background: var(--gradient-primary);
        border-radius: 50%;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
        animation: pulse 2s ease-in-out infinite alternate;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.5); }
        100% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.8); }
    }

    .answer-text {
        color: var(--text-primary);
        line-height: 1.8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }

    /* Advanced copy button with ripple effect */
    .copy-button {
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem 2rem !important;
        transition: var(--transition-smooth) !important;
        min-width: 150px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.75rem !important;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
    }

    .copy-button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transition: width 0.6s, height 0.6s, top 0.6s, left 0.6s;
        transform: translate(-50%, -50%);
    }

    .copy-button:active::before {
        width: 300px;
        height: 300px;
        top: 50%;
        left: 50%;
    }

    .copy-button:hover {
        background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 
            0 8px 30px rgba(16, 185, 129, 0.4),
            0 0 40px rgba(16, 185, 129, 0.2) !important;
    }

    /* Progress bar with glow effect */
    .stProgress > div > div {
        background: var(--gradient-primary) !important;
        border-radius: 10px !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.5) !important;
    }

    .stProgress > div {
        background: var(--background-surface) !important;
        border-radius: 10px !important;
    }

    /* Advanced expander styling */
    .streamlit-expander {
        background: var(--glass-bg) !important;
        backdrop-filter: var(--backdrop-blur) !important;
        border: 2px solid var(--glass-border) !important;
        border-radius: var(--border-radius) !important;
        margin-bottom: 2rem !important;
        overflow: hidden;
        transition: var(--transition-smooth);
    }

    .streamlit-expander:hover {
        border-color: var(--primary-color) !important;
        box-shadow: var(--shadow-glow);
        transform: translateY(-2px);
    }

    .streamlit-expanderHeader {
        padding: 1.5rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        color: var(--primary-light) !important;
        background: var(--gradient-surface) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: var(--border-radius) var(--border-radius) 0 0 !important;
        position: relative;
    }

    .streamlit-expanderContent {
        padding: 2rem !important;
        background: var(--glass-bg) !important;
    }

    /* Responsive design improvements */
    @media (max-width: 768px) {
        :root {
            --border-radius: 12px;
            --border-radius-small: 8px;
            --border-radius-large: 16px;
        }
        
        .stApp {
            padding-top: 1rem !important;
        }
        
        .main .block-container {
            padding: 1rem 0.75rem !important;
        }
        
        h1 {
            font-size: 2.5rem !important;
        }
        
        .subtitle {
            font-size: 1.1rem !important;
            margin-bottom: 2rem !important;
        }
        
        .answer-card {
            padding: 1.5rem !important;
            margin: 1.5rem 0 !important;
        }
        
        .stButton > button {
            padding: 0.875rem 1.5rem !important;
            font-size: 0.9rem !important;
        }
        
        .stFileUploader {
            padding: 2rem !important;
        }
    }

    /* Accessibility improvements with better focus indicators */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible {
        outline: 3px solid var(--primary-color) !important;
        outline-offset: 3px !important;
        box-shadow: 0 0 0 6px rgba(99, 102, 241, 0.2) !important;
    }

    /* Hide file uploader remove buttons */
    .stFileUploader button[kind="secondary"],
    .stFileUploader button[data-testid="stButton"]:not([type="button"]),
    .stFileUploader .stButton:not([type="button"]),
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

    /* File uploader button styling */
    .stFileUploader button[type="button"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem 2rem !important;
        transition: var(--transition-smooth) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3) !important;
        text-transform: none !important;
        letter-spacing: 0.025em !important;
        margin: 1rem auto 0 auto !important;
        position: relative !important;
        overflow: hidden !important;
        display: block !important;
        width: auto !important;
        min-width: 180px !important;
    }

    .stFileUploader button[type="button"]:hover {
        background: var(--gradient-secondary) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: var(--shadow-hover) !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--background-secondary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--gradient-primary);
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--gradient-secondary);
    }

    /* Selection styling */
    ::selection {
        background: rgba(99, 102, 241, 0.3);
        color: var(--text-primary);
    }

    ::-moz-selection {
        background: rgba(99, 102, 241, 0.3);
        color: var(--text-primary);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Enhanced title with animated subtitle
    st.markdown(
        f"""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="margin-bottom: 0.5rem;">
            {svg_icons['brain']} Hire Helper
        </h1>
        <div class="subtitle" style="position: relative;">
            Your AI-powered interview preparation companion
            <div style="position: absolute; top: -20px; right: -20px; animation: float 3s ease-in-out infinite;">
                {svg_icons['sparkles']}
            </div>
        </div>
    </div>
    
    <style>
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-10px) rotate(180deg); }}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Prepare API keys dictionary
    api_keys_dict = {
        "Google": GOOGLE_API_KEY,
        "OpenAI": OPENAI_API_KEY,
        "Claude": ANTHROPIC_API_KEY,
    }

    # Check if at least one API key is available
    available_providers = [provider for provider, key in api_keys_dict.items() if key]

    # If no API keys are found in environment, show BYOK interface
    if not available_providers:
        st.warning("No API keys found in environment variables.")

        st.markdown("### Bring Your Own API Keys")
        st.markdown("**Enter your API keys to get started:**")
        st.markdown(
            "You only need **one** API key to use Hire Helper. Choose your preferred provider:"
        )

        # Provider comparison table
        with st.expander("Provider Comparison", expanded=False):
            comparison_data = {
                "Provider": ["Google Gemini", "OpenAI GPT", "Anthropic Claude"],
                "Free Tier": ["Generous", "Limited trial", "Limited trial"],
                "Best Models": ["Gemini 2.0 Flash", "GPT-4o", "Claude 3.5 Sonnet"],
                "Pricing": [
                    "$0-0.075/1K tokens",
                    "$0.50-60/1M tokens",
                    "$3-75/1M tokens",
                ],
                "Strengths": [
                    "Fast, multimodal",
                    "Versatile, popular",
                    "Thoughtful, ethical",
                ],
            }

            st.table(comparison_data)
            st.markdown(
                "**Recommendation**: Start with Google Gemini for the best free tier!"
            )

            # Add use case recommendations
            st.markdown("### Which Provider Should You Choose?")

            rec_col1, rec_col2 = st.columns(2)

            with rec_col1:
                st.markdown("**Choose Google Gemini if:**")
                st.markdown("• You want to try for free")
                st.markdown("• You need the latest AI capabilities")
                st.markdown("• You want fast response times")
                st.markdown("• You're processing multiple documents")

                st.markdown("**Choose OpenAI GPT if:**")
                st.markdown("• You need maximum compatibility")
                st.markdown("• You're familiar with ChatGPT")
                st.markdown("• You're using this for business")

            with rec_col2:
                st.markdown("**Choose Anthropic Claude if:**")
                st.markdown("• You need thoughtful, nuanced responses")
                st.markdown("• You're working with complex writing tasks")
                st.markdown("• You prioritize safety and ethics")
                st.markdown("• You need detailed analysis")

                st.markdown("**Pro Tip:**")
                st.markdown(
                    "Start with Google Gemini's free tier, then upgrade to paid services if you need more volume or specific capabilities!"
                )

            # Quick setup guides
            st.markdown("### Quick Setup Guides")

            setup_col1, setup_col2, setup_col3 = st.columns(3)

            with setup_col1:
                st.markdown("**Google Gemini Setup:**")
                st.markdown(
                    "1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)"
                )
                st.markdown("2. Click 'Create API Key'")
                st.markdown("3. Copy the key (starts with AIza)")
                st.markdown("4. Paste it in the Google field below")

            with setup_col2:
                st.markdown("**OpenAI Setup:**")
                st.markdown(
                    "1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)"
                )
                st.markdown("2. Click 'Create new secret key'")
                st.markdown("3. Copy the key (starts with sk-)")
                st.markdown("4. Paste it in the OpenAI field below")

            with setup_col3:
                st.markdown("**Anthropic Setup:**")
                st.markdown(
                    "1. Go to [Anthropic Console](https://console.anthropic.com/)"
                )
                st.markdown("2. Create an account and add credits")
                st.markdown("3. Generate API key (starts with sk-ant-)")
                st.markdown("4. Paste it in the Claude field below")

        # Provider status and instructions
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Google Gemini**")
            st.markdown("• Free tier available")
            st.markdown(
                "• Get key from [Google AI Studio](https://aistudio.google.com/app/apikey)"
            )
            google_key_input = st.text_input(
                "Google API Key",
                type="password",
                help="Get your key from Google AI Studio (aistudio.google.com)",
                placeholder="AIza...",
                key="byok_google",
                value=st.session_state.saved_api_keys.get("Google", ""),
            )
            if google_key_input and not google_key_input.startswith("AIza"):
                st.warning("Google API keys typically start with 'AIza'")
            elif google_key_input:
                st.session_state.saved_api_keys["Google"] = google_key_input

        with col2:
            st.markdown("**OpenAI GPT**")
            st.markdown("• Paid service")
            st.markdown(
                "• Get key from [OpenAI Platform](https://platform.openai.com/api-keys)"
            )
            openai_key_input = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Get your key from OpenAI Platform (platform.openai.com)",
                placeholder="sk-...",
                key="byok_openai",
                value=st.session_state.saved_api_keys.get("OpenAI", ""),
            )
            if openai_key_input and not openai_key_input.startswith("sk-"):
                st.warning("OpenAI API keys start with 'sk-'")
            elif openai_key_input:
                st.session_state.saved_api_keys["OpenAI"] = openai_key_input

        with col3:
            st.markdown("**Anthropic Claude**")
            st.markdown("• Paid service")
            st.markdown(
                "• Get key from [Anthropic Console](https://console.anthropic.com/)"
            )
            claude_key_input = st.text_input(
                "Anthropic API Key",
                type="password",
                help="Get your key from Anthropic Console (console.anthropic.com)",
                placeholder="sk-ant-...",
                key="byok_claude",
                value=st.session_state.saved_api_keys.get("Claude", ""),
            )
            if claude_key_input and not claude_key_input.startswith("sk-ant-"):
                st.warning("Anthropic API keys start with 'sk-ant-'")
            elif claude_key_input:
                st.session_state.saved_api_keys["Claude"] = claude_key_input

        # Update API keys dictionary with user inputs
        if google_key_input:
            api_keys_dict["Google"] = google_key_input
        if openai_key_input:
            api_keys_dict["OpenAI"] = openai_key_input
        if claude_key_input:
            api_keys_dict["Claude"] = claude_key_input

        # Update available providers
        available_providers = [
            provider for provider, key in api_keys_dict.items() if key
        ]

        # Show status
        if available_providers:
            provider_status = []
            for provider in ["Google", "OpenAI", "Claude"]:
                if provider in available_providers:
                    provider_status.append(f"Available: {provider}")
                else:
                    provider_status.append(f"Not set: {provider}")

            st.info(f"**Provider Status:** {' | '.join(provider_status)}")
            st.success(
                f"Ready to go with {', '.join(available_providers)} provider(s)!"
            )

            # Add button to clear saved keys
            if st.button(
                "Clear Saved API Keys", help="Clear all API keys from this session"
            ):
                st.session_state.saved_api_keys = {
                    "Google": "",
                    "OpenAI": "",
                    "Claude": "",
                }
                st.rerun()

            # Add API key testing
            with st.expander("Test API Keys (Optional)", expanded=False):
                st.markdown("Test your API keys to make sure they work:")

                for provider in available_providers:
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**{provider}** API Key")

                    with col2:
                        test_button_key = f"test_{provider.lower()}_key"
                        if st.button(
                            f"Test {provider}",
                            key=test_button_key,
                            help=f"Test your {provider} API key",
                        ):
                            with st.spinner(f"Testing {provider} API key..."):
                                # Get the first available model for testing
                                test_models = {
                                    "Google": "gemini-1.5-flash",
                                    "OpenAI": "gpt-3.5-turbo",
                                    "Claude": "claude-3-haiku-20240307",
                                }
                                test_model = test_models[provider]

                                is_valid, message = test_api_key(
                                    provider, api_keys_dict[provider], test_model
                                )

                                if is_valid:
                                    st.success(f"{provider}: {message}")
                                else:
                                    st.error(f"{provider}: {message}")
        else:
            st.error("Please enter at least one valid API key to continue.")
            st.stop()
    else:
        # Show option to override environment keys
        with st.expander("Override API Keys (Optional)", expanded=False):
            st.markdown("**Override environment variables with custom keys:**")
            st.info(
                "**Tip:** Your environment already has API keys configured. You can optionally override them here."
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"**Google:** {'Available' if api_keys_dict['Google'] else 'Not set'}"
                )
                google_key_input = st.text_input(
                    "Google API Key",
                    type="password",
                    help="Override GOOGLE_API_KEY environment variable",
                    placeholder="Leave empty to use env var",
                    key="override_google",
                )
                if google_key_input and not google_key_input.startswith("AIza"):
                    st.warning("Google API keys typically start with 'AIza'")

            with col2:
                st.markdown(
                    f"**OpenAI:** {'Available' if api_keys_dict['OpenAI'] else 'Not set'}"
                )
                openai_key_input = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Override OPENAI_API_KEY environment variable",
                    placeholder="Leave empty to use env var",
                    key="override_openai",
                )
                if openai_key_input and not openai_key_input.startswith("sk-"):
                    st.warning("OpenAI API keys start with 'sk-'")

            with col3:
                st.markdown(
                    f"**Claude:** {'Available' if api_keys_dict['Claude'] else 'Not set'}"
                )
                claude_key_input = st.text_input(
                    "Anthropic API Key",
                    type="password",
                    help="Override ANTHROPIC_API_KEY environment variable",
                    placeholder="Leave empty to use env var",
                    key="override_claude",
                )
                if claude_key_input and not claude_key_input.startswith("sk-ant-"):
                    st.warning("Anthropic API keys start with 'sk-ant-'")

            # Update API keys dictionary with user inputs if provided
            if google_key_input:
                api_keys_dict["Google"] = google_key_input
            if openai_key_input:
                api_keys_dict["OpenAI"] = openai_key_input
            if claude_key_input:
                api_keys_dict["Claude"] = claude_key_input

            # Update available providers
            available_providers = [
                provider for provider, key in api_keys_dict.items() if key
            ]

            # Show current status
            provider_status = []
            for provider in ["Google", "OpenAI", "Claude"]:
                if provider in available_providers:
                    provider_status.append(f"Available: {provider}")
                else:
                    provider_status.append(f"Not set: {provider}")

            st.info(f"**Current Status:** {' | '.join(provider_status)}")

        # Configuration summary outside the expander
        if available_providers:
            st.markdown("### Configuration Summary")
            st.markdown("**Your Current Setup:**")
            st.markdown(f"• **Available Providers:** {', '.join(available_providers)}")
            st.markdown(
                f"• **Environment Keys:** {len([k for k in [GOOGLE_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY] if k])} configured"
            )
            st.markdown(
                f"• **Session Keys:** {len([k for k in st.session_state.saved_api_keys.values() if k])} entered"
            )
            st.markdown(
                "• **Ready to Process:** Yes"
                if available_providers
                else "• **Ready to Process:** No"
            )

    is_mobile = st.checkbox(
        "Mobile view", value=False, help="Check this for better mobile experience"
    )

    if is_mobile:
        st.markdown("---")

        with st.expander("Configuration", expanded=True):
            st.markdown(
                f"""
            <div style="text-align: center; margin-bottom: 2rem; color: var(--text-accent);">
                {svg_icons['upload']} <strong>Upload Your Resume</strong>
            </div>
            """,
                unsafe_allow_html=True,
            )

            uploaded_resume = st.file_uploader(
                "Upload Your Resume",
                type=["txt", "md", "pdf", "docx"],
                help="Supported formats: TXT, MD, PDF, DOCX",
                key=f"mobile_uploader_{st.session_state.file_uploader_key}",
                label_visibility="collapsed",
            )

            # Add clear resume button for mobile
            if uploaded_resume:
                st.success(f"**Uploaded:** {uploaded_resume.name}")
                if st.button(
                    "Clear Resume",
                    key="clear_resume_mobile",
                    help="Remove the uploaded resume file",
                ):
                    # Clear the file uploader by incrementing the key
                    st.session_state.file_uploader_key += 1
                    st.rerun()

            # Model selection for mobile
            col1, col2 = st.columns(2)
            with col1:
                model_provider = st.selectbox(
                    "AI Model Provider",
                    options=available_providers,
                    index=0,
                    key="mobile_provider",
                    help="Choose your AI model provider",
                )

            with col2:
                model_name = st.selectbox(
                    "Model",
                    options=model_options.get(model_provider, []),
                    index=0,
                    key="mobile_model",
                    help="Choose the specific model",
                )

                if model_name in model_descriptions:
                    st.caption(model_descriptions[model_name])

                # Show cost estimation in mobile
                if st.checkbox(
                    "Show Cost Estimates",
                    help="Estimate costs for your current configuration",
                    key="mobile_cost_check",
                ):
                    # Get rough estimates for cost calculation
                    estimated_resume_length = (
                        2000  # Average resume length in characters
                    )
                    num_questions = len(
                        [q for q in st.session_state.questions if q.strip()]
                    )

                    if num_questions > 0:
                        estimated_cost = estimate_cost(
                            model_provider,
                            model_name,
                            estimated_resume_length,
                            num_questions,
                            word_limit if "word_limit" in locals() else 100,
                        )

                        st.info(f"**Estimated Cost:** {estimated_cost}")
                        st.caption(
                            "*Based on average resume size and current questions*"
                        )

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

        st.sidebar.markdown(
            f"""
        <div style="text-align: center; margin-bottom: 1.5rem; color: var(--text-accent);">
            {svg_icons['upload']} <strong>Upload Your Resume</strong>
        </div>
        """,
            unsafe_allow_html=True,
        )

        uploaded_resume = st.sidebar.file_uploader(
            "Upload Your Resume",
            type=["txt", "md", "pdf", "docx"],
            help="Supported formats: TXT, MD, PDF, DOCX",
            key=f"desktop_uploader_{st.session_state.file_uploader_key}",
            label_visibility="collapsed",
        )

        # Add clear resume button for desktop
        if uploaded_resume:
            st.sidebar.success(f"**Uploaded:** {uploaded_resume.name}")
            if st.sidebar.button(
                "Clear Resume",
                key="clear_resume_desktop",
                help="Remove the uploaded resume file",
            ):
                # Clear the file uploader by incrementing the key
                st.session_state.file_uploader_key += 1
                st.rerun()

        # Model selection for desktop
        model_provider = st.sidebar.selectbox(
            "AI Model Provider",
            options=available_providers,
            index=0,
            key="desktop_provider",
            help="Choose your AI model provider",
        )

        model_name = st.sidebar.selectbox(
            "Model",
            options=model_options.get(model_provider, []),
            index=0,
            key="desktop_model",
            help="Choose the specific model",
        )

        if model_name in model_descriptions:
            st.sidebar.caption(model_descriptions[model_name])

        # Show cost estimation in sidebar
        if st.sidebar.checkbox(
            "Show Cost Estimates", help="Estimate costs for your current configuration"
        ):
            # Get rough estimates for cost calculation
            estimated_resume_length = 2000  # Average resume length in characters
            num_questions = len([q for q in st.session_state.questions if q.strip()])

            if num_questions > 0:
                estimated_cost = estimate_cost(
                    model_provider,
                    model_name,
                    estimated_resume_length,
                    num_questions,
                    word_limit if "word_limit" in locals() else 100,
                )

                st.sidebar.info(f"**Estimated Cost:** {estimated_cost}")
                st.sidebar.caption(
                    "*Based on average resume size and current questions*"
                )

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
        model_provider = st.session_state.mobile_provider
        model_name = st.session_state.mobile_model
    else:
        user_additional_company_info = user_additional_company_info_desktop
        model_provider = st.session_state.desktop_provider
        model_name = st.session_state.desktop_model

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

            # Enhanced progress bar with animated loading
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Add a loading animation
                st.markdown(
                    """
                <div style="text-align: center; margin: 2rem 0;">
                    <div style="display: inline-block; animation: spin 2s linear infinite;">
                        """
                    + svg_icons["brain"]
                    + """
                    </div>
                    <p style="margin-top: 1rem; color: var(--text-secondary);">AI is working on your personalized responses...</p>
                </div>
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )

            try:

                status_text.markdown("**Step 1:** Processing your resume...")
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
                        status_text.markdown(
                            "**Step 2:** AI is formatting your resume..."
                        )
                        progress_bar.progress(60)
                        resume_text = format_resume_text_with_llm(
                            raw_resume_text, model_provider, model_name, api_keys_dict
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

                status_text.markdown(f"**Step 3:** Researching {company}...")
                progress_bar.progress(70)
                company_research_data = ""
                if company.strip():
                    company_research_data = get_company_research(company, api_keys_dict)

                if company_research_data and company.strip():
                    with st.expander(
                        f"Initial Research Findings for {company}",
                        expanded=False,
                    ):
                        st.markdown(company_research_data)

                status_text.markdown(
                    "**Step 4:** AI is crafting your personalized answers..."
                )
                progress_bar.progress(90)

                valid_questions = [
                    q.strip() for q in st.session_state.questions if q.strip()
                ]
                if not valid_questions:
                    st.warning("Please ensure at least one question is filled out.")
                    st.stop()

                answers = generate_answers(
                    resume_text,
                    role,
                    company,
                    valid_questions,
                    word_limit,
                    model_provider,
                    model_name,
                    api_keys_dict,
                    user_additional_company_info,
                    company_research_data,
                )

                progress_bar.progress(100)
                status_text.markdown("**Complete!** Your answers are ready")

                # Clear the loading animation
                progress_container.empty()

                if answers:
                    st.markdown(
                        f"""
                    <div style="text-align: center; margin: 2rem 0; padding: 2rem; background: var(--glass-bg); 
                         backdrop-filter: var(--backdrop-blur); border-radius: var(--border-radius-large); 
                         border: 2px solid var(--success);">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">{svg_icons['check']}</div>
                        <h2 style="color: var(--success); margin: 0;">Your personalized interview answers are ready!</h2>
                        <p style="color: var(--text-secondary); margin-top: 0.5rem;">
                            Tailored specifically for {role} at {company}
                        </p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Enhanced JavaScript for clipboard functionality
                    copy_js = (
                        """
                    function copyToClipboard(textToCopy, buttonId) {
                        const fallbackCopy = (text) => {
                            const textArea = document.createElement("textarea");
                            textArea.value = text;
                            textArea.style.top = "0";
                            textArea.style.left = "0";
                            textArea.style.position = "fixed";
                            document.body.appendChild(textArea);
                            textArea.focus();
                            textArea.select();

                            let success = false;
                            try {
                                success = document.execCommand('copy');
                            } catch (err) {
                                console.error('Fallback: Unable to copy', err);
                            }

                            document.body.removeChild(textArea);
                            return Promise.resolve(success);
                        };

                        const button = document.getElementById(buttonId);
                        if (!button) return;
                        const originalText = button.innerHTML;
                        const originalClass = button.className;

                        if (!navigator.clipboard) {
                            fallbackCopy(textToCopy).then((success) => {
                                if (success) {
                                    button.innerHTML = '"""
                        + svg_icons["check"]
                        + """ Copied!';
                                    button.className = originalClass + ' copy-button-copied';
                                    setTimeout(() => { 
                                        button.innerHTML = originalText; 
                                        button.className = originalClass;
                                    }, 2000);
                                } else {
                                    alert('Failed to copy text. Please copy manually.');
                                }
                            });
                            return;
                        }

                        navigator.clipboard.writeText(textToCopy).then(() => {
                            button.innerHTML = '"""
                        + svg_icons["check"]
                        + """ Copied!';
                            button.className = originalClass + ' copy-button-copied';
                            setTimeout(() => { 
                                button.innerHTML = originalText; 
                                button.className = originalClass;
                            }, 2000);
                        }).catch(err => {
                            console.error('Clipboard API failed: ', err);
                            fallbackCopy(textToCopy).then((success) => {
                                if (success) {
                                    button.innerHTML = '"""
                        + svg_icons["check"]
                        + """ Copied!';
                                    button.className = originalClass + ' copy-button-copied';
                                    setTimeout(() => { 
                                        button.innerHTML = originalText; 
                                        button.className = originalClass;
                                    }, 2000);
                                } else {
                                    alert('Failed to copy text. Please copy manually.');
                                }
                            });
                        });
                    }
                    """
                    )
                    st.markdown(f"<script>{copy_js}</script>", unsafe_allow_html=True)

                    for i, item in enumerate(answers, start=1):
                        # Ensure text is properly escaped for JS
                        answer_text_json = json.dumps(item["answer"])
                        button_id = f"copy_button_{i}"

                        st.markdown(
                            f"""<div class="answer-card">
                                <div class="question-header">
                                    <span>Question {i}</span>
                                </div>
                                <div style="color: var(--text-accent); margin-bottom: 1.5rem; font-style: italic; 
                                     font-size: 1.1rem; line-height: 1.6; padding: 1rem; 
                                     background: rgba(99, 102, 241, 0.1); border-radius: var(--border-radius-small); 
                                     border-left: 4px solid var(--primary-color);">
                                    "{item['question']}"
                                </div>
                                <div class="answer-text">
                                    <strong style="color: var(--primary-light); font-size: 1.1rem;">Your Answer:</strong><br><br>
                                    {item['answer']}
                                </div>
                                <button id="{button_id}" class="copy-button" onclick='copyToClipboard({answer_text_json}, "{button_id}")'>
                                    {svg_icons['copy']} Copy Answer
                                </button>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        # Add some space after each card
                        st.markdown("<br>", unsafe_allow_html=True)

                else:
                    st.info("ℹ️ No questions were provided to generate answers for.")

            except Exception as e:
                progress_container.empty()
                st.error(f"An error occurred during answer generation: {e}")
                st.error("Please try again or check your inputs.")


if __name__ == "__main__":
    main()
