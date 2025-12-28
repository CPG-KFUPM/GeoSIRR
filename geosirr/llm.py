import os
import base64
import requests
import openai
import ollama
from . import io
from . import vis
from typing import List, Dict, Optional, Union, Tuple
import matplotlib.pyplot as plt
from datetime import datetime
# Enable interactive mode for matplotlib
plt.ion()


# Function to create a file with the Files API
def create_file(client, file_path):
  with open(file_path, "rb") as file_content:
    result = client.files.create(
        file=file_content,
        purpose="vision",
    )
    return result.id
  

def load_openai_api_key() -> str:
    """
    Load the OpenAI API key from environment variable.

    Returns
    -------
    :obj:`str`
        The OpenAI API key.

    Raises
    ------
    ValueError
        If OPENAI_API_KEY environment variable is not set.
    """
    # First check environment variable
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key.strip()
    
    raise ValueError("OPENAI_API_KEY environment variable not set.")


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Estimate the number of tokens in a text string for a given model.

    Parameters
    ----------
    text : :obj:`str`
        The input text.
    model : :obj:`str`, optional
        The model name (used for tokenizer selection). Default is 'gpt-4'.

    Returns
    -------
    :obj:`int`
        Estimated token count.
    """
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except ImportError:
        print("tiktoken not installed, falling back to naive token estimation.")
        return len(text.split())
    except Exception:
        # For non-OpenAI models, use rough estimate (1 token ≈ 4 characters)
        return max(1, len(text) // 4)


def get_openai_models() -> List[str]:
    """
    Retrieve a list of available OpenAI models.
    
    Returns
    -------
    :obj:`list`
        List of model names.
    """    

    api_key = load_openai_api_key()
    client = openai.OpenAI(api_key=api_key)

    try:
        resp = client.models.list()
    except Exception:
        # Some OpenAI-compatible providers may not support listing models.
        return []

    data = getattr(resp, "data", None)
    if data is None and isinstance(resp, dict):
        data = resp.get("data")

    if not data:
        return []

    model_ids: List[str] = []
    for item in data:
        if hasattr(item, "id"):
            model_ids.append(str(item.id))
        elif isinstance(item, dict) and "id" in item:
            model_ids.append(str(item["id"]))

    return sorted(set(model_ids))


def get_ollama_models() -> List[str]:
    """
    Retrieve a list of available Ollama models.

    Returns
    -------
    :obj:`list`
        List of model names.
    """
    if not is_ollama_running():
        raise RuntimeError("Ollama is not running. Please start it before calling this function.")

    listing = ollama.list()
    models = listing.get("models", []) if isinstance(listing, dict) else []
    names: List[str] = []
    for m in models:
        if isinstance(m, dict):
            if "model" in m:
                names.append(str(m["model"]))
            elif "name" in m:
                names.append(str(m["name"]))

    return sorted(set(n for n in names if n))


def validate_llm(llm_backend: str, llm_name: str, client: Optional[openai.OpenAI] = None) -> bool:
    """
    Validate if the specified LLM backend and model name are supported.

    Parameters
    ----------
    llm_backend : :obj:`str`
        The LLM backend, either 'openai' or 'ollama'.
    llm_name : :obj:`str`
        The LLM model name, e.g. 'gpt-5' or 'gemma3:27b'.
    client : Optional[:obj:`openai.OpenAI`]
        Optional OpenAI client (used for validation when backend is 'openai').
    
    Returns
    -------
    True if valid, False otherwise.
    """
    if llm_backend is None:
        raise ValueError("llm_backend must be provided.")
    backend = str(llm_backend).strip().lower()

    if not llm_name or not str(llm_name).strip():
        raise ValueError("llm_name must be a non-empty string.")
    model = str(llm_name).strip()

    if backend not in {"openai", "ollama"}:
        raise ValueError(f"Unsupported LLM backend: {llm_backend}. Choose 'openai' or 'ollama'.")

    if backend == "openai":
        # Ensure API key is present
        load_openai_api_key()

        if client is not None and not isinstance(client, openai.OpenAI):
            raise ValueError("client must be an instance of openai.OpenAI or None.")

        # Best-effort model existence check.        
        available = get_openai_models()
        
    elif backend == "ollama":
        # Ollama backend
        if not is_ollama_running():
            raise RuntimeError("Ollama is not running. Please start it before using backend='ollama'.")

        available = get_ollama_models()

    # Check if model is in available list (if available list is non-empty)
    if not available:
        print("Warning: Could not retrieve model list for validation. Assuming model is valid.")
        return True
    elif available and model not in available:
        print(f"Model '{model}' not found in available models for '{backend}' backend.")
        print("Available models are:")
        for m in available:
            print(f" - {m}")
        return False
    else:
        return True
    

def encode_image_to_data_uri(path: str) -> str:
    """
    Load an image file and return a Base64 Data URI.

    Parameters
    ----------
    path : :obj:`str`
        Path to the image file.
    
    Returns
    -------
    :obj:`str`
        Base64 Data URI for the image, e.g. "data:image/png;base64,...".
    """
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    return f"data:image/{ext};base64,{encoded}"


def call_openai_response(
    client: openai.OpenAI,    
    model: str,
    input: List[Dict[str, str]],        
    images: Optional[Union[str, List[str]]] = None,
    files: Optional[Union[str, List[str]]] = None,    
    **kwargs
) -> tuple[dict, List[Dict[str, str]]]:
    r"""
    Call the OpenAI API for a chat response.

    Parameters
    ----------
    client : :obj:`openai.OpenAI`
        The OpenAI API client.
    model : :obj:`str`
        The model to use for the response.
    input : List[Dict[str, str]]
        The input messages to send to the API.    
    images : Optional[Union[:obj:`str`, List[:obj:`str`]]], optional
        List of image file paths to upload (if supported by the model) or a single image path.
    files : Optional[Union[:obj:`str`, List[:obj:`str`]]], optional
        List of file paths to upload (if supported by the model) or a single file path.

    Returns
    -------
    :obj:`dict`
        The API response.
    :obj:`list`
        The input messages sent to the API.
    """
    # Check if the client is initialized
    if not isinstance(client, openai.OpenAI):
        raise ValueError("client must be an instance of OpenAI.")
    
    # If images are provided, create IDs for them
    if images:
        image_ids = []
        if isinstance(images, str):
            images = [images]
        for image_path in images:
            if not os.path.isfile(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            image_id = create_file(client, image_path)
            image_ids.append(image_id)
    else:
        image_ids = None

    # If files are provided, create IDs for them
    if files:
        file_ids = []
        if isinstance(files, str):
            files = [files]
        for file_path in files:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            file_id = create_file(client, file_path)
            file_ids.append(file_id)
    else:
        file_ids = None

    # Update the user input block with images and files
    if file_ids is not None or image_ids is not None:
        user_text = input[-1]["content"]

        # Prepare user content
        user_content = [{"type": "input_text", "text": user_text}]
        if file_ids:
            user_content += [{"type": "input_file", "file_id": file_id} for file_id in file_ids]
        if image_ids:
            user_content += [{"type": "input_image", "file_id": image_id} for image_id in image_ids]

        # Compose user block
        user_block = {
            "role": "user",
            "content": user_content,
        }

        # Replace the last user message in input with the new user block
        input[-1] = user_block

    # Call the API
    api_args = {
        "model": model,
        "input": input,
        **kwargs
    }

    # Always attempt to add reasoning (some models like gpt-5.2 support it)
    # If the model doesn't support it, the try/except block below will handle the fallback
    api_args["reasoning"] = {
        "effort": "medium",
        "summary": "auto",
    }

    try:
        response = client.responses.create(**api_args)
    except Exception as e:
        # Fallback: if reasoning parameter causes error, try without it
        if "reasoning" in api_args and ("Unsupported parameter" in str(e) or "unexpected keyword argument" in str(e)):
            del api_args["reasoning"]
            response = client.responses.create(**api_args)
        else:
            raise e
    
    return response, input

def call_llm(
    backend: str,
    model: str,        
    input: List[Dict[str, str]],
    image_paths: Optional[List[str]] = None,
    **kwargs
    ):
    r"""
    Universal function to call different LLM backends (Ollama, OpenAI),
    optionally uploading images.

    Parameters
    ----------
    backend : :obj:`str`
        One of 'openai' or 'ollama'.
    model : :obj:`str`
        LLM model name (e.g. 'gemma3:27b' or 'gpt-5').
    input : List[Dict[str, str]]
        A list of input dicts with 'role' and 'content'.
    image_paths : Optional[List[:obj:`str`]]
        Paths to image files to upload (if supported by backend).
    **kwargs
        Additional parameters passed to the underlying API call.

    Raises
    ------
    ValueError
        If an unsupported backend is specified.

    Returns
    -------
    :obj:`dict` or :obj:`ollama.ChatResponse` or :obj:`ollama.GenerateResponse` or :obj:`openai.responses.response.Response`
        The raw response from the selected backend.
    """
    backend = backend.lower()
    # OpenAI Backend
    if backend == "openai":
        # Load and set API key
        api_key = load_openai_api_key()
        
        # Determine Base URL based on model
        base_url = None
        is_deepseek = "deepseek" in model.lower()
        is_gemini = "gemini" in model.lower()
        is_standard_gpt = any(m in model.lower() for m in ["gpt-4", "gpt-3.5", "o1-"])
        
        if is_deepseek:
            base_url = "https://api.deepseek.com"
        elif is_gemini:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            
        openai.api_key = api_key
        if base_url:
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = openai.OpenAI(api_key=api_key)

        # If using alternative providers or standard GPT models, use standard chat completions
        if is_deepseek or is_gemini or is_standard_gpt:
            # Prepare messages (copy to avoid mutating original)
            messages = [m.copy() for m in input]
            
            # Handle images if present (convert to base64)
            if image_paths:
                # Assuming the last message is user message where we append images
                last_msg = messages[-1]
                if last_msg["role"] == "user":
                    content = last_msg["content"]
                    new_content = [{"type": "text", "text": content}]
                    
                    for img_path in image_paths:
                        data_uri = encode_image_to_data_uri(img_path)
                        new_content.append({
                            "type": "image_url",
                            "image_url": {"url": data_uri}
                        })
                    
                    last_msg["content"] = new_content
                    messages[-1] = last_msg
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response, messages

        # Use the response API for chat completions
        response, input = call_openai_response(client=client, 
                        model=model, 
                        input=input,
                        images=image_paths)

        return response, input

    # Ollama Backend
    if backend == "ollama":        
        # Check if ollama is running
        if not is_ollama_running():
            raise RuntimeError("Ollama is not running. Please start it before calling this function.")
        # Use ollama's chat API with or without images
        if image_paths:
            files = {os.path.basename(p): open(p, "rb") for p in image_paths}
            response = ollama.chat(
                model=model,
                messages=input,
                files=files,
                **kwargs
            )
        else:
            response = ollama.chat(
                model=model,
                messages=input,
                **kwargs
            )

        return response, input

    raise ValueError(f"Unsupported backend: {backend}. Choose 'openai' or 'ollama'.")


def initialize_ollama() -> str:
    r"""
    Reads the OLLAMA_HOST environment variable and returns its value (base URL for local Ollama API).

    Returns
    -------
    :obj:`str`
        The base URL for the Ollama API, ensuring it has no trailing slash.
    """
    host = os.environ.get("OLLAMA_HOST")
    if not host:
        print("OLLAMA_HOST environment variable not set, using default 'http://localhost:11434'.")
        host = "http://localhost:11434"
    # Ensure no trailing slash
    return host.rstrip("/")

def is_ollama_running(host: str = "http://localhost:11434", timeout: float = 0.5) -> bool:
    r"""
    Checks if the Ollama server is running by sending a GET request to the base URL.

    Parameters
    ----------
    host : :obj:`str`, optional
        The base URL for the Ollama API. Default is "http://localhost:11434".
    timeout : :obj:`float`, optional
        The timeout for the request in seconds. Default is 0.5 seconds.
    Returns
    -------
    :obj:`bool`
        True if the server is running and responds with a 200 status code, False otherwise.
    """
    host = initialize_ollama()
    try:
        resp = requests.get(f"{host}/", timeout=timeout)
        return resp.status_code == 200
    except requests.RequestException:
        return False

def parse_response(
    response: Union[
        ollama.ChatResponse,
        ollama.GenerateResponse,
        openai.types.responses.response.Response,
        dict  # openai responses come back as dicts (or objects with .choices)
    ]
) -> Tuple[str, Optional[str]]:
    """
    Parses responses from Ollama or OpenAI (both Completion & Chat) to extract the generated text,
    and pulls out any <think>…</think> reasoning block separately.

    Parameters
    ----------
    response : :obj:`ollama.ChatResponse` or :obj:`ollama.GenerateResponse` or :obj:`openai.types.responses.response.Response` or :obj:`dict`
        The raw response from Ollama or OpenAI.

    Returns
    -------
    text : :obj:`str`
        The generated text with any <think>…</think> section removed.
    reasoning_text : :obj:`str` or None
        The content inside <think>…</think>, if present.
    """
    # Initialize reasoning variable
    reasoning = None

    # Ollama Chat
    if isinstance(response, ollama.ChatResponse):
        full = response["message"]["content"].strip()

    # Ollama Generate
    elif isinstance(response, ollama.GenerateResponse):
        full = response.get("response", "").strip()        
    # OpenAI-style response with .output_text attribute
    elif isinstance(response, openai.types.responses.response.Response):
        full = response.output_text.strip()
            
        # Find the reasoning item in response.output
        reasoning_item = next(
            (item for item in response.output if item.type == "reasoning"),
            None
        )

        # Extract the summary text from that item
        if reasoning_item and reasoning_item.summary:
            # .summary is a list of Summary objects; each has a .text field.
            reasoning = "".join(part.text for part in reasoning_item.summary)
        else:
            reasoning = None

    # OpenAI-style dict response
    elif isinstance(response, dict) and "choices" in response:
        choice = response["choices"][0]
        # ChatCompletion
        if isinstance(choice, dict) and "message" in choice:
            full = choice["message"]["content"].strip()
        # Completion
        else:
            full = choice.get("text", "").strip()

    # OpenAI-style object with .choices attribute
    elif hasattr(response, "choices"):
        choice = response.choices[0]
        # ChatCompletionChoice
        if hasattr(choice, "message"):
            full = choice.message.content.strip()
        # CompletionChoice
        else:
            full = choice.text.strip()

    else:
        raise ValueError(f"Unrecognized response type: {type(response)}")

    # Now split out any <think>…</think> block
    if reasoning is None:
        if "<think>" in full and "</think>" in full:
            start = full.index("<think>")
            end = full.index("</think>") + len("</think>")
            reasoning = full[start + len("<think>") : full.index("</think>")].strip()
            # remove the entire <think>…</think> block
            cleaned = (full[:start] + full[end:]).strip()
        else:
            cleaned = full
    else:
        cleaned = full

    return cleaned, reasoning


def generate_section_text(instruction_prompt: str,
                          text: str,
                          image_files: list[str] = None,
                          llm_backend: str = "openai",
                          llm_name: str = "gpt-5",
                          llm_params: dict = None,
                          max_gen_iterations: int = 5,
                          max_chats: int = 3,
                          only_prompt: bool = False,
                          section_preview: bool = False,
                          verbose: bool = True):
    r"""
    Generates a cross section of a geological model text format
    based on a user instruction prompt, text description and images.

    Parameters
    ----------
    instruction_prompt : :obj:`str`
        The user instruction prompt for generating the cross section.
    text : :obj:`str`
        The text as a string
    image_files : :obj:`list[str]`, optional
        List of image filenames
    llm_backend : :obj:`str`, optional
        The backend to use for LLM generation, e.g., "ollama". Default is "ollama".
    llm_name : :obj:`str`, optional
        The name of the LLM to use for generation. Default is "gemma3:12b".
    llm_params : :obj:`dict`, optional
        Additional parameters for the LLM generation, such as temperature and top_p.
    max_gen_iterations : :obj:`int`, optional
        Maximum number of iterations to attempt generation in one chat. Default is 5.
    max_chats : :obj:`int`, optional
        Maximum number of chat attempts to generate the section. Default is 3.
    only_prompt : :obj:`bool`, optional
        If True, only returns the prompt without generating the section. Default is False.
    section_preview : :obj:`bool`, optional
        If True, visualizes a preview of the section if the format is valid. Default is False.
    verbose : :obj:`bool`, optional
        If True, prints additional information during the generation process. Default is True.

    Returns
    -------
    success :obj:`bool`
        True if the section was generated successfully, False otherwise.
    section_content :obj:`str`
        The generated model section as a string, if `only_prompt` is False, otherwise empty string.
    full_prompt : :obj:`str`
        The full prompt used for generating the section, useful for debugging or logging.
    chats :obj:`list[list[dict]]`
        The chats exchanged during the generation process, useful for debugging or logging.

    Raises
    ------
    ValueError
        If text is empty
    ValueError
        If max_gen_iterations is not a positive integer.
    """
    # Check maximum number of iterations
    if max_gen_iterations <= 0:
        raise ValueError("max_gen_iterations must be a positive integer.")
    # Check maximum number of chats
    if max_chats <= 0:
        raise ValueError("max_chats must be a positive integer.")
    # Check if text is not empty
    if not text.strip():
        raise ValueError("The provided text is empty. Please provide valid text.")

    # Define role
    llm_role = "You are a highly advanced expert geologist with highly developed imagination that allow you to understand text descriptions of geological cross sections and recreate their geometries digitally. " \
    "When you answer, put your chain-of-thought inside <think>...</think>, then after that give the final answer."

    # Build prompt
    prompt_sections = [
        "Read the following, take your time and be sure to understand the task before generating the cross section.",
        "",
        "## Your task",
        "",
        "You are tasked in generating valid geological cross sections relevant to the description in special text format described below. You must thoroughly follow these instructions.",
        "",
        io.adjust_markdown_headers(instruction_prompt, level=2),
        "",
        "## **Description of the geological model cross section to be created**",
        "",
        io.adjust_markdown_headers(text, level=3),
    ]

    # Add image filenames if any
    if image_files:
        prompt_sections.extend([
            "",
            "### Cross section visuals",
            "",
            "Here is the list of images which help you to understand the geological cross section better:",
            "\n".join(os.path.basename(f) for f in image_files),
        ])

    # Final prompt section
    prompt_sections.extend(["",
        "## Final remarks",
        "",
        "Now, based on the description above, please produce the complete full cross section in all necessary details following the given instructions.",
        "Your answer MUST contain ONLY the content of the cross section out inside the fenced code block.",
        "All commentaries, if you find them useful, must be put inside the code block after # symbol, as it is explained by the format specification.",
        "This is important because your answer will be automatically checked for correctness and if you don't place your answer inside the fenced code block, it will be considered as invalid.",
    ])

    # Join all sections into a single prompt
    user_prompt = "\n".join(prompt_sections)

    # Initialize chats list
    chats = []

    # Combine llm_role and user_prompt into full_prompt
    full_prompt = f"## Your role\n\n{llm_role}\n\n{user_prompt}"

    # Print full prompt if verbose
    if verbose:
        print("-------------------------------------------------------")
        print(text)        
        print("-------------------------------------------------------")
        llm_role_token_count = count_tokens(llm_role, model=llm_name)
        print(f"Token count estimate for the LLM role prompt: {llm_role_token_count} tokens")
        user_prompt_token_count = count_tokens(user_prompt, model=llm_name)
        print(f"Token count estimate for the user prompt: {user_prompt_token_count} tokens")
        print("-------------------------------------------------------")
        if only_prompt:
            print("\nOnly prompt requested, skipping generation.")
            return True, "", full_prompt, chats

        print(f"\nStarting cross section generation with {llm_backend} using the following parameters:")
        print(f"LLM Name: {llm_name}")
        if llm_params is not None:
            print(f"LLM Parameters: {llm_params}")

    # Initialize success flag
    success = False

    # Attempt multiple chats
    for chat_idx in range(1, max_chats + 1):
        if verbose:
            print(f"Starting chat {chat_idx}/{max_chats}...")
        # Initialize conversation history for this chat
        input = [
            {"role": "system", "content": llm_role},
            {"role": "user", "content": user_prompt}
        ]

        # Inner loop: generation attempts within one chat
        for attempt in range(1, max_gen_iterations + 1):
            if verbose:
                print(f"  Attempt {attempt}/{max_gen_iterations} in chat {chat_idx}...")
            response, input = call_llm(
                backend=llm_backend,
                model=llm_name,
                input=input,
                image_paths=image_files,
                **({"options": llm_params} if llm_params else {})
            )
            out_content, reasoning_text = parse_response(response)

            # Display generated content if verbose
            if verbose:
                if reasoning_text:
                    print(f"Reasoning text (length {len(reasoning_text)} characters):\n{reasoning_text}")
                print(f"Generated content (length {len(out_content)} characters):\n{out_content}")                
                output_token_count = count_tokens(out_content, model=llm_name)
                print(f"Token count estimate for output content: {output_token_count} tokens")

            # Clean fences
            section_content = io.clean_code_block_markers(out_content)

            # Validate the cleaned content format
            is_valid_format, format_errors = io.validate_cross_section_format(section_content)

            # Prepare format errors string
            if not is_valid_format:
                format_errors_string = "Format errors:\n" + "\n".join(str(x) for x in format_errors)
            else:
                format_errors_string = ""

            # Try to validate the topology
            try:
                is_valid_topology, topology_errors = io.validate_cross_section_topology(section_content)
                # Prepare topology errors string
                if not is_valid_topology:
                    topology_errors_string = "Topology errors:\n" + "\n".join(str(x) for x in topology_errors)
                else:
                    topology_errors_string = ""
            except Exception as e:
                is_valid_topology = False
                topology_errors_string = ""

            if is_valid_format and section_preview:
                if is_valid_topology:
                    topology_label = ""
                else:
                    topology_label = " (invalid topology)"
                gendate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                vis.plot_cross_section(section_content,
                    title=f'Generated by {llm_name} on {gendate} (chat {chat_idx}, attempt {attempt}){topology_label}')

            # If valid format and topology, return the cleaned content
            if is_valid_format and is_valid_topology:
                success = True
                if reasoning_text:
                     input.append({"role": "assistant", "content": f"<think>{reasoning_text}</think>\n{section_content}"})
                else:
                    input.append({"role": "assistant", "content": section_content})
                chats.append(input)
                if section_preview:
                    plt.show()
                if verbose:
                    print("Success: a valid cross-section has been generated.")
                return success, section_content, full_prompt, chats

            # Prepare error messages string
            errors_string = f"{format_errors_string}\n{topology_errors_string}"

            # If invalid, append feedback to conversation
            feedback = [
                "The generated cross section is invalid.",
                errors_string,
                "Please revise the output to conform to the required format and ensure correct topology.",
                "Keep in mind that the cross section must be a valid geological model representation which is consistent with the provided geological context.",
                "Again, your answer MUST contain ONLY the full revised content of the whole cross section inside the fenced code block.",
                "All commentaries, if you find them useful, must be put inside the code block after # symbol, as it is explained by the format specification.",
            ]
            # Join feedback messages
            feedback_message = "\n".join(feedback)
            if verbose:
                print(f"Invalid cross section detected.\nUser feedback:\n{feedback_message}")

            # Append feedback to messages
            input.append({"role": "assistant", "content": section_content})
            input.append({"role": "user", "content": feedback_message})

        # Append messages to chat history
        chats.append(input)

        # End of attempts for this chat, proceed to next chat
        if verbose:
            print(f"Chat {chat_idx} exhausted without success.")
    # Show section preview if requested
    # if section_preview:
        # plt.show()
    return success, "", full_prompt, chats
