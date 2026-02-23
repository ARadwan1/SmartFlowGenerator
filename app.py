import streamlit as st
import os

# We use the new google-genai SDK
from google import genai
from google.genai import types

# Set page config
st.set_page_config(page_title="Smart Flow Generator", page_icon="✈️", layout="wide")

st.title("✈️ Amadeus Smart Flow Generator")
st.markdown("Describe the travel workflow you want to automate, and AI will generate the Smart Flow Advanced Language script.")

# API Key handling
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Get your API key from Google AI Studio")
if not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to continue.")
    st.stop()

# Initialize the client
client = genai.Client(api_key=api_key)

# Read the skills file
@st.cache_data
def load_skills():
    try:
        # Assumes the app is run from the exact directory where the skills file lives
        with open("SmartFlow_Skills.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

skills_context = load_skills()
if not skills_context:
    st.error("Error: Could not find `SmartFlow_Skills.md` in the current directory.")
    st.stop()

# Build System Instruction
system_instruction = f"""You are an expert Amadeus Selling Platform Connect developer. 
Your task is to write syntactically correct 'Smart Flow Advanced Language' scripts based on user requests.
Follow the rules, syntax, and terminal capture coordinates provided in the skills document below.

CRITICAL RULES:
1. ONLY output valid Smart Flow code.
2. DO NOT wrap the code in markdown formatting like ```smartflow ... ```, just output the raw code. (Or if you do, wrap it in plain text block so the UI strips it easily, but raw is better).
3. Follow the best practices, modularity, and error handling as defined.
4. If the user asks for coordinates for a specific Amadeus screen, use the exact ones provided in your knowledge base.

=== SKILLS KNOWLEDGE BASE ===
{skills_context}
"""

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.2, # Low temperature for code generation
)

# User input
user_prompt = st.text_area("Describe your Smart Flow:", height=150, placeholder="e.g. Prompt the user for a passenger name, send 'RT', capture the 6-character PNR locator, and put it in a 'RM' command...")

if st.button("Generate Smart Flow", type="primary"):
    if not user_prompt.strip():
        st.error("Please enter a description.")
    else:
        with st.spinner("Generating your script..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=user_prompt,
                    config=config,
                )
                
                script = response.text
                
                # Cleanup markdown blocks if the model accidentally adds them
                if script.startswith("```smartflow"):
                    script = script.replace("```smartflow", "").strip()
                elif script.startswith("```"):
                    script = script[3:].strip()
                if script.endswith("```"):
                    script = script[:-3].strip()

                st.subheader("Generated Script")
                st.code(script, language="javascript") # Streamlit supports JS syntax highlighting which is close enough to Smart Flow
                
                st.success("Successfully generated! Use the copy button in the top right of the code block above.")
                
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
