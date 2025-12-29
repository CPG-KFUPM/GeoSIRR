import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import geosirr as gs
import templates
import clarification

# Constants
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
OUTPUT_DIR = "output"
PROMPTS_DIR = os.path.join("prompts")
SECTION_PROMPT_FILE = os.path.join(PROMPTS_DIR, "section_text_generation.md")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("================================================================")
    print(" GeoSIRR")    
    print(" Geological Section Interpretation, Reconstruction & Refinement")
    print(" Version:", gs.__version__)
    print(" --------------------------------------------------------------")
    print(" This app generates geological cross-sections:)")
    print(" from textual descriptions.")
    print(" It uses Large Language Models (LLMs) developed by OpenAI.")
    print(" --------------------------------------------------------------")
    print(" Developed by Denis Anikiev and Juan Mosquera, KFUPM, 2025")
    print(" GitHub: https://github.com/CPG-KFUPM/GeoSIRR")
    print("================================================================")
    print("")

def get_api_key():
    """Get API key from .env file or user input."""
    # 1. Try to load from .env file
    load_dotenv(ENV_FILE)
    key = os.environ.get("OPENAI_API_KEY")
    
    if key and key != "your_api_key_here":
        return key

    # 2. If not found, ask user
    print("OpenAI API Key not found in .env file.")
    key = input("Please enter your OpenAI API Key: ").strip()
    
    if key:
        # Save to .env for future use
        try:
            with open(ENV_FILE, "w") as f:
                f.write(f"OPENAI_API_KEY={key}")
            print(f"API Key saved to {ENV_FILE}")
            # Also set in current environment
            os.environ["OPENAI_API_KEY"] = key
        except Exception as e:
            print(f"Warning: Could not save to {ENV_FILE}: {e}")
            
        return key
    else:
        print("An OpenAI API Key is required to proceed.")
        sys.exit(1)

def ensure_directories():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(PROMPTS_DIR):
        os.makedirs(PROMPTS_DIR)

def select_model():
    """Allow user to select the LLM model."""
    models = [
        "gpt-5",
        "gpt-5.1",
        "gpt-5.2",
    ]
    
    print("\nSelect an LLM from OpenAI (gpt-5 is recommended):")
    for i, m in enumerate(models):
        print(f"{i+1}. {m}")
    print(f"{len(models)+1}. Enter custom LLM name")
    print("Use 0 to exit application.")
    
    while True:        
        choice = input("\nEnter choice (default 1): ").strip()
        if not choice:
            return models[0]
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                print(f"Selected model: {models[idx]}")
                return models[idx]
            elif idx == len(models):
                custom_model = input("Enter custom LLM name: ").strip()
                if not gs.llm.validate_llm(llm_backend="openai", llm_name=custom_model):
                    print(f"The specified model {custom_model} is not recognized.")
                    raise ValueError("Invalid model name.") 
                return custom_model
            elif idx == -1:
                print("Exiting...")
                sys.exit(0)
            else:
                print("Invalid selection. Please enter a number.")
        except ValueError:
            print("Please try again.")
                

def select_template():
    print("\nAvailable Templates:")
    template_names = list(templates.TEMPLATES.keys())
    for i, name in enumerate(template_names):
        print(f"{i+1}. {name}")
    
    while True:
        try:
            choice = input("\nSelect a template (number) or 'c' to cancel: ").strip()
            if choice.lower() == 'c':
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(template_names):
                return templates.TEMPLATES[template_names[idx]]
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

def process_description(description, api_key, model_name):
    """
    Process the description: Clarify -> Generate -> Validate -> Plot
    """
    os.environ["OPENAI_API_KEY"] = api_key
    
    print(f"\n--- Using Model: {model_name} ---")
    
    print("\n--- Validating Description ---")
    validation = clarification.validate_description(description, llm_model=model_name)
    
    print(f"Status: {validation.get('status', 'unknown')}")
    print(f"Confidence: {validation.get('confidence', 0)}%")
    
    if validation.get('status') != 'complete':
        print("\nIssues found:")
        for missing in validation.get('missing_critical', []):
            print(f"- CRITICAL: {missing}")
        for suggestion in validation.get('suggestions', []):
            print(f"- Suggestion: {suggestion}")
            
        if validation.get('clarification_question'):
            print(f"\nClarification needed: {validation.get('clarification_question')}")
            
        proceed = input("\nDo you want to proceed anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Operation cancelled. Please refine your description.")
            return

    print("\n--- Generating Cross Section ---")
    print("This may take a minute...")
    
    # Read system prompt
    try:
        with open(SECTION_PROMPT_FILE, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(f"Error: System prompt file not found at {SECTION_PROMPT_FILE}")
        return
    
    # Save timestamp for file naming
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Save original description for reference
    try:        
        description_filename = f"description_{timestamp}.md"
        description_filepath = os.path.join(OUTPUT_DIR, description_filename)
        with open(description_filepath, "w", encoding="utf-8") as f:
            f.write(description)
        print(f"User description saved to: {description_filepath}")
    except Exception as e:
        print(f"Warning: Could not save description file: {e}")
    
    # Generate section
    try:
        success, text_result, full_prompt, _ = gs.llm.generate_section_text(
            instruction_prompt=system_prompt,
            text=description,
            image_files=None,
            llm_backend="openai",
            llm_name=model_name,
            llm_params=None,
            max_gen_iterations=5,
            max_chats=1,
            only_prompt=False,
            section_preview=False,
            verbose=True
        )
        
        if not success:
            print("\nGeneration failed.")
            return
        else:
            # Save full prompt for reference
            prompt_filename = f"full_prompt_{timestamp}.md"
            prompt_filepath = os.path.join(OUTPUT_DIR, prompt_filename)
            with open(prompt_filepath, "w", encoding="utf-8") as f:
                f.write(full_prompt)
            print(f"Full prompt saved to: {prompt_filepath}")            

        print("\n--- Validating Result ---")
        is_valid_format, format_errors = gs.io.validate_cross_section_format(text_result)
        
        if not is_valid_format:
            print("Format Validation Failed:")
            for err in format_errors:
                print(f"- {err}")
            return
        else:
            print("Format Validation: PASSED")
            
        is_valid_topology, topology_errors = gs.io.validate_cross_section_topology(text_result)
        if not is_valid_topology:
            print("Topology Validation Failed:")
            for err in topology_errors:
                print(f"- {err}")
            # We might still want to plot it to show the error
            print("Attempting to plot despite topology errors...")
        else:
            print("Topology Validation: PASSED")

        # Save result
        gen_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"section_{gen_timestamp}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(text_result)
        print(f"\nResult saved to: {filepath}")

        # Plot
        print("\n--- Plotting ---")
        try:
            fig, ax = gs.vis.plot_cross_section(
                definition=text_result,
                title=f"Generated Section - {gen_timestamp}",
                filename=os.path.join(OUTPUT_DIR, f"section_{gen_timestamp}.png")
            )
            print("Plot window opening...")
            plt.show()
            print("Plot closed.")
        except Exception as e:
            print(f"Error plotting: {e}")
            
        # Refinement Loop
        while True:
            print("\nOptions:")
            print("0. Exit the application")
            print("1. Refine this section")
            print("2. Ask a question about this section")
            print("3. Return to Main Menu")            
            
            refine_choice = input("\nEnter choice (0-3): ").strip()
            
            if refine_choice == '1':
                refinement = input("\nEnter refinement instructions: ").strip()
                if refinement:
                    # Append refinement to description and re-process
                    # Note: Ideally we would pass the previous result as context, 
                    # but for now we append to the prompt.
                    new_description = f"{description}\n\nRefinement Request: {refinement}"
                    process_description(new_description, api_key, model_name)
                    return # Exit this instance of process_description to avoid deep recursion stack
            elif refine_choice == '2':
                question = input("\nEnter your question about the section: ").strip()
                if question:
                    answer = clarification.ask_about_section(
                        question=question,
                        definition=text_result,
                        description=description,
                        api_key=api_key,
                        llm_model=model_name
                    )
                    if answer:
                        print(f"\nAnswer:\n{answer}")
                    else:
                        print("Failed to get an answer.")
            elif refine_choice == '3':
                return
            elif refine_choice == '0':
                print("Exiting...")
                sys.exit(0)
            else:
                print("Invalid choice.")

    except Exception as e:
        print(f"An error occurred during generation: {e}")
        import traceback
        traceback.print_exc()


def main():
    ensure_directories()
    clear_screen()
    print_header()
    
    api_key = get_api_key()
    model_name = select_model()
    
    while True:
        print("\nMain Menu:")
        print("0. Exit the application")
        print("1. Run Example (Select from Templates)")
        print("2. Enter Custom Description")
                
        choice = input("\nEnter choice (0-2): ").strip()
        
        if choice == '1':
            template = select_template()
            if template:
                print(f"\nSelected Template:\n{template[:100]}...")
                process_description(template, api_key, model_name)
        
        elif choice == '2':
            print("\nEnter your geological description (press Enter on an empty line to finish):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            description = "\n".join(lines).strip()
            
            if description:
                print("\nProcessing description...")
                process_description(description, api_key, model_name)
            else:
                print("Empty description.")
                
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
