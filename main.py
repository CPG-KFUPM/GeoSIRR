import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime

import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import clarification
import geosirr as gs
import templates

# Constants
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
OUTPUT_DIR = "output"
PROMPTS_DIR = os.path.join("prompts")
SECTION_PROMPT_FILE = os.path.join(PROMPTS_DIR, "section_text_generation.md")


class _RunLogger:
    """Record stage and total runtimes for one generation workflow."""

    def __init__(self, timestamp, backend, model_name):
        self.path = os.path.join(OUTPUT_DIR, f"run_{timestamp}.log")
        self.backend = backend
        self.model_name = model_name
        self.started_at = datetime.now().astimezone()
        self.started_clock = time.perf_counter()
        self.stages = []
        self.finished = False

    @contextmanager
    def stage(self, name):
        record = {
            "name": name,
            "start_time": datetime.now().astimezone(),
            "status": "success",
        }
        started_clock = time.perf_counter()
        try:
            yield record
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            record["end_time"] = datetime.now().astimezone()
            record["runtime_seconds"] = time.perf_counter() - started_clock
            self.stages.append(record)
            print(f"{name.replace('_', ' ').title()} runtime: {record['runtime_seconds']:.2f} s")

    def finish(self, status):
        if self.finished:
            return
        self.finished = True
        ended_at = datetime.now().astimezone()
        runtime = time.perf_counter() - self.started_clock
        if status == "success" and any(stage["status"] == "failed" for stage in self.stages):
            status = "completed_with_errors"

        lines = [
            "GeoSIRR generation run",
            f"status: {status}",
            f"backend: {self.backend}",
            f"model: {self.model_name}",
            f"start_time: {self.started_at.isoformat(timespec='seconds')}",
            f"end_time: {ended_at.isoformat(timespec='seconds')}",
            f"runtime_seconds: {runtime:.6f}",
            "stages:",
        ]
        for stage in self.stages:
            lines.extend(
                [
                    f"  - name: {stage['name']}",
                    f"    status: {stage['status']}",
                    f"    start_time: {stage['start_time'].isoformat(timespec='seconds')}",
                    f"    end_time: {stage['end_time'].isoformat(timespec='seconds')}",
                    f"    runtime_seconds: {stage['runtime_seconds']:.6f}",
                ]
            )
            if stage.get("error"):
                lines.append(f"    error: {stage['error']}")

        try:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            print(f"Run log saved to: {self.path}")
        except OSError as exc:
            print(f"Warning: Could not save run log: {exc}")
        print(f"Total workflow runtime: {runtime:.2f} s")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("================================================================")
    print(" GeoSIRR")    
    print(" Geological Section Interpretation, Reconstruction & Refinement")
    print(" Version:", gs.__version__)
    print(" --------------------------------------------------------------")
    print(" This app generates geological cross-sections")
    print(" from textual descriptions.")
    print(" It uses Large Language Models (LLMs) via OpenAI or Ollama.")
    print(" --------------------------------------------------------------")
    print(" Developed by Denis Anikiev and Juan Mosquera, KFUPM, 2025-2026")
    print(" GitHub: https://github.com/CPG-KFUPM/GeoSIRR")
    print("================================================================")
    print()

def get_openai_api_key():
    """Get OpenAI API key from .env file or user input."""
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


def select_backend():
    """Allow user to select LLM backend/provider."""
    print("\nSelect LLM provider:")
    print("1. OpenAI (cloud)")
    print("2. Ollama (local)")
    print("Use 0 to exit application.")

    while True:
        choice = input("\nEnter choice (default 1): ").strip()
        if not choice:
            return "openai"
        if choice == "1":
            return "openai"
        if choice == "2":
            return "ollama"
        if choice == "0":
            print("Exiting...")
            sys.exit(0)
        print("Invalid selection. Please enter 0, 1, or 2.")


def setup_backend(backend):
    """Prepare provider-specific runtime settings and checks."""
    if backend == "openai":
        return get_openai_api_key()

    if backend == "ollama":
        load_dotenv(ENV_FILE)
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").strip()
        os.environ["OLLAMA_HOST"] = host
        if not gs.llm.is_ollama_running(host):
            print(f"Ollama server is not running at {host}.")
            print("Please start Ollama and try again.")
            print("Example: `ollama serve` and then `ollama pull gemma4:e4b`")
            sys.exit(1)
        print(f"Ollama detected at {host}.")
        return None

    raise ValueError(f"Unsupported backend: {backend}")

def ensure_directories():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(PROMPTS_DIR):
        os.makedirs(PROMPTS_DIR)

def select_model(backend):
    """Allow user to select the LLM model for the selected backend."""
    if backend == "openai":
        models = [
            "gpt-5.6",
            "gpt-5.5",
            "gpt-5.4",
            "gpt-5.3",
            "gpt-5.2",
            "gpt-5.1",
            "gpt-5",
        ]
    elif backend == "ollama":
        try:
            models = gs.llm.get_ollama_models()
        except Exception as e:
            print(f"Could not retrieve Ollama models: {e}")
            models = []
    else:
        raise ValueError(f"Unsupported backend: {backend}")

    if backend == "openai":
        print("\nSelect an LLM from OpenAI (gpt-5 is recommended):")
    else:
        print("\nSelect an LLM from Ollama (local models):")

    if models:
        for i, m in enumerate(models):
            print(f"{i+1}. {m}")
        print(f"{len(models)+1}. Enter custom LLM name")
    else:
        print("No local models were discovered. Enter a custom model name.")
        print("Example: llama3.1:8b")

    print("Use 0 to exit application.")

    while True:
        if models:
            choice = input("\nEnter choice (default 1): ").strip()
            if not choice:
                print(f"Selected model: {models[0]}")
                return models[0]

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    print(f"Selected model: {models[idx]}")
                    return models[idx]
                if idx == len(models):
                    custom_model = input("Enter custom LLM name: ").strip()
                elif idx == -1:
                    print("Exiting...")
                    sys.exit(0)
                else:
                    print("Invalid selection. Please enter a number.")
                    continue
            except ValueError:
                print("Please try again.")
                continue
        else:
            custom_model = input("Enter model name (or 0 to exit): ").strip()
            if custom_model == "0":
                print("Exiting...")
                sys.exit(0)

        if not custom_model:
            print("Model name cannot be empty.")
            continue

        if not gs.llm.validate_llm(llm_backend=backend, llm_name=custom_model):
            print(f"The specified model {custom_model} is not recognized.")
            continue

        print(f"Selected model: {custom_model}")
        return custom_model
                

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

def process_description(description, api_key, llm_backend, model_name, last_refinement=None, last_result=None):
    """
    Process the description: Clarify -> Generate -> Validate -> Plot
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_log = _RunLogger(timestamp, llm_backend, model_name)

    if llm_backend == "openai" and api_key:
        os.environ["OPENAI_API_KEY"] = api_key
   
    print(f"\n--- Using Backend: {llm_backend} ---")
    print(f"--- Using Model: {model_name} ---")
    
    print("\n--- Validating Description ---")
    try:
        with run_log.stage("description_validation"):
            validation = clarification.validate_description(
                description,
                llm_model=model_name,
                llm_backend=llm_backend,
            )
    except Exception:
        run_log.finish("error")
        raise
    
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
            run_log.finish("cancelled")
            return

    print("\n--- Generating Cross Section ---")
    print("This may take a minute...")
    
    # Read system prompt
    try:
        with run_log.stage("prompt_loading"):
            with open(SECTION_PROMPT_FILE, "r", encoding="utf-8") as f:
                system_prompt = f.read()
    except FileNotFoundError:
        print(f"Error: System prompt file not found at {SECTION_PROMPT_FILE}")
        run_log.finish("prompt_loading_failed")
        return

    # Save original description for reference
    with run_log.stage("description_saving") as stage:
        try:
            description_filename = f"description_{timestamp}.md"
            description_filepath = os.path.join(OUTPUT_DIR, description_filename)
            with open(description_filepath, "w", encoding="utf-8") as f:
                f.write(description)
            print(f"User description saved to: {description_filepath}")
        except OSError as e:
            stage["status"] = "failed"
            stage["error"] = f"{type(e).__name__}: {e}"
            print(f"Warning: Could not save description file: {e}")
    
    # Generate section
    try:
        with run_log.stage("cross_section_generation"):
            success, text_result, full_prompt, _ = gs.llm.generate_section_text(
                instruction_prompt=system_prompt,
                text=description,
                image_files=None,
                llm_backend=llm_backend,
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
            run_log.finish("generation_failed")
            return
        else:
            # Save full prompt for reference
            with run_log.stage("prompt_saving"):
                prompt_filename = f"full_prompt_{timestamp}.md"
                prompt_filepath = os.path.join(OUTPUT_DIR, prompt_filename)
                with open(prompt_filepath, "w", encoding="utf-8") as f:
                    f.write(full_prompt)
                print(f"Full prompt saved to: {prompt_filepath}")

        print("\n--- Validating Result ---")
        with run_log.stage("result_validation") as stage:
            is_valid_format, format_errors = gs.io.validate_cross_section_format(text_result)

            if not is_valid_format:
                stage["status"] = "failed"
                stage["error"] = "Format validation failed: " + "; ".join(format_errors)
                print("Format Validation Failed:")
                for err in format_errors:
                    print(f"- {err}")
            else:
                print("Format Validation: PASSED")
                is_valid_topology, topology_errors = gs.io.validate_cross_section_topology(text_result)
                if not is_valid_topology:
                    stage["status"] = "failed"
                    stage["error"] = "Topology validation failed: " + "; ".join(topology_errors)
                    print("Topology Validation Failed:")
                    for err in topology_errors:
                        print(f"- {err}")
                    # We might still want to plot it to show the error
                    print("Attempting to plot despite topology errors...")
                else:
                    print("Topology Validation: PASSED")

        if not is_valid_format:
            run_log.finish("validation_failed")
            return

        # Save result
        gen_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with run_log.stage("result_saving"):
            filename = f"section_{gen_timestamp}.txt"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text_result)
            print(f"\nResult saved to: {filepath}")

        # Plot
        print("\n--- Plotting ---")
        plot_ready = False
        with run_log.stage("plot_rendering") as stage:
            try:
                gs.vis.plot_cross_section(
                    definition=text_result,
                    title=f"Generated Section - {gen_timestamp}",
                    filename=os.path.join(OUTPUT_DIR, f"section_{gen_timestamp}.png")
                )
                plot_ready = True
            except Exception as e:
                stage["status"] = "failed"
                stage["error"] = f"{type(e).__name__}: {e}"
                print(f"Error plotting: {e}")

        run_log.finish("success")

        if plot_ready:
            print("Plot window opening...")
            plt.show()
            print("Plot closed.")
            
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
                    # Append refinement and previous result to the description and re-process
                    if last_refinement:
                        new_refinement = last_refinement + f"\n\nResult of the previous refinement:\n{text_result}\n---\nRefinement request: {refinement}\n" 
                    else:
                        new_refinement = f"Result of the previous generation:\n{text_result}\n---\nRefinement Request: {refinement}\n"
                    new_description = f"{description}\n\n{new_refinement}"                    
                    process_description(new_description, api_key, llm_backend, model_name, new_refinement)
                    return # Exit this instance of process_description to avoid deep recursion stack
            elif refine_choice == '2':
                question = input("\nEnter your question about the section: ").strip()
                if question:
                    answer = clarification.ask_about_section(
                        question=question,
                        definition=text_result,
                        description=description,
                        api_key=api_key,
                        llm_model=model_name,
                        llm_backend=llm_backend,
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
        run_log.finish("error")
        print(f"An error occurred during generation: {e}")
        import traceback
        traceback.print_exc()


def main():
    ensure_directories()
    clear_screen()
    print_header()
    
    llm_backend = select_backend()
    api_key = setup_backend(llm_backend)
    model_name = select_model(llm_backend)
    
    while True:
        print("\nMain Menu:")
        print("0. Exit the application")
        print("1. Run Example (Select from Templates)")
        print("2. Enter Custom Description")
                
        choice = input("\nEnter choice (0-2): ").strip()
        
        if choice == '1':
            template = select_template()
            if template:
                #print(f"\nSelected Template:\n{template[:100]}...")
                print(f"\nSelected Template:\n{template}...")
                process_description(template, api_key, llm_backend, model_name)
        
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
                process_description(description, api_key, llm_backend, model_name)
            else:
                print("Empty description.")
                
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
