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

# Read the skills file. We load it dynamically every time so new user rules take immediate effect.
def load_skills():
    try:
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

# UI Layout Tabs
tab1, tab2 = st.tabs(["🚀 Generator & Prompt Wizard", "🧠 Teach the AI (Add Rules)"])

with tab1:
    st.markdown("### 1. Build Your Prompt")
    
    col1, col2 = st.columns([1, 1])
    
    # Initialize session state for prompt if not exists
    if "prompt" not in st.session_state:
        st.session_state.prompt = ""
        
    def set_prompt(text):
        st.session_state.prompt = text
    
    with col1:
        st.subheader("Quick Templates")
        if st.button("TWD / Ticket Pricing Flow"):
            set_prompt("Create a Smart Flow to ask the user for a ticket number (enforcing a hyphen). Then format a TWD/TKT command with the number. Finally, use Fallback Capturing to search for the word TOTAL dynamically and display the amount.")
        
        if st.button("Add Passenger Info"):
            set_prompt("Create a Smart Flow to ask for Family Name and First Name, then format and send an NM1 command.")

        if st.button("EMD Base Fare Capture"):
            set_prompt("Create a Smart Flow to ask for an EMD number, send an EWD command, and use Fallback Capturing to find the base FARE value dynamically.")
            
    with col2:
        st.subheader("Prompt Wizard")
        with st.expander("Build Prompt Step-by-Step"):
            wi_goal = st.text_input("Main goal? (e.g., Read ticket and sum amounts)")
            wi_inputs = st.text_input("Questions for agent? (e.g., Ticket Number)")
            wi_commands = st.text_input("Cryptic commands? (e.g., TWD/TKT)")
            wi_captures = st.text_input("Data to capture? (e.g., Total Fare via Fallback)")
            
            if st.button("Compile into Prompt"):
                compiled_text = f"Goal: {wi_goal}\nAgent Prompts: {wi_inputs}\nCommands: {wi_commands}\nCaptures Required: {wi_captures}\nPlease generate the smart flow."
                set_prompt(compiled_text)
                
    st.divider()
    
    user_prompt = st.text_area("2. Your Final Prompt (Edit if needed):", value=st.session_state.prompt, height=150)

    if st.button("Generate Smart Flow", type="primary", use_container_width=True):
        if not user_prompt.strip():
            st.error("Please build or enter a description in the text area above.")
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
                    st.code(script, language="javascript")
                    
                    st.success("Successfully generated! Use the copy button in the top right of the code block above.")
                except Exception as e:
                    st.error(f"Error generating content: {str(e)}")

with tab2:
    st.header("Teach the AI new rules")
    st.markdown("Did the AI make a mistake or miss a specific Amadeus command syntax? Add a golden rule here. It will be **permanently** added to its knowledge base, making it smarter for everyone.")
    
    new_rule = st.text_area("Describe the correct behavior/logic:", placeholder="Example: When issuing an EMD, never use TWD, always use EWD and capture the base fare.", height=150)
    
    if st.button("Add to AI Knowledge Base", type="primary"):
        if new_rule.strip():
            with open("SmartFlow_Skills.md", "a", encoding="utf-8") as file:
                file.write("\n\n### User Added Rule / Correction:\n")
                file.write(new_rule.strip() + "\n")
            st.success("Rule added successfully! The AI will now use this knowledge in all future generations. No restart needed.")
        else:
            st.error("Please write a rule first.")
