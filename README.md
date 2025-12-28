# GeoSIRR

Geological Section Interpretation, Reconstruction & Refinement

## Overview

GeoSIRR is a Python-based tool for generating, interpreting, refining, and visualizing geological cross-sections using Large Language Models ([LLMs]).
This command-line interface (CLI) version allows users to generate geological models from text descriptions without the need for a web interface.

The application performs the following steps:

1. Validates the user's geological description for completeness.
2. Generates a structured text representation of the cross-section using OpenAI's GPT models.
3. Validates the generated output for format and topological correctness.
4. Visualizes the result using Matplotlib.

## Prerequisites

- Python 3.12
- [PIP] package manager
- An [OpenAI] API Key

## Installation

To install packages you can use either [pip], [conda] or any other package manager.
Below are the instructions for [pip](#installation-using-pip) and [conda](#installation-using-conda).

### Installation using pip

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Installation using conda

Create a new conda environment and install the required packages from the provided `environment.yml` file. This file contains all the necessary Python dependencies.

Type this command, for instance, in [Miniforge] prompt:

```bash
conda env create -f environment.yml
```

or just

```bash
conda env create
```

Then activate the environment:

```bash
conda activate geosirr
```

## Configuration

This application requires an OpenAI API key to function.

1. Locate or create the `.env` file in the root application directory.
2. Open the file with a text editor.
3. Add your actual API key like that:

   ```plaintext
   OPENAI_API_KEY=sk-proj-123456789...
   ```

4. Save the file.

Alternatively, if the `.env` file is not configured, the application will prompt you to enter your API key upon startup and will save it to a local file for future use.

## Usage

To start the application, run the following command in your terminal:

```bash
python main.py
```

### Select LLM

Upon startup, you will be prompted to select an LLM from a list of three most relevant models, e.g.:

1. gpt-5.2
2. gpt-5.1
3. gpt-5

you can also enter a custom LLM name if your desired model is not listed (option 4).

If you select a custom LLM name, the application will validate whether the specified model is recognized. If the model is not recognized, a list of valid models will be displayed, and you can use option 4 again to re-enter a valid model name.

Select 0 to exit the application.

### Main Menu

Upon selecting the [LLM], you will have the following options:

1. **Run Example (Select from Templates)**
   - Choose from a list of pre-defined geological scenarios (e.g., Normal Fault, Thrust Fault, etc.).
   - This is recommended for first-time users to test the system.

2. **Enter Custom Description**
   - Type or paste your own geological description.
   - Press Enter twice to submit the description.

Option 0 exits the application.

### Output

When you run a generation, the application will produce both text and image files representing the geological cross-section. The cross-section image will also be displayed in a pop-up window.

Generated files are saved in the `output` directory.

- **Text Files (.txt):** Contain the coordinate and polygon definitions of the cross-section.
- **Image Files (.png):** Visualizations of the generated cross-sections.

Files are named with a timestamp (e.g., `section_2025-12-26_10-30-00.png`) to prevent overwriting.

### Refining Sections

After generating a section, you can choose to refine it by providing additional instructions (e.g., "Make the fault steeper" or "Add more layers"). The application will update the section accordingly and save the new output files.

## Troubleshooting

**Issue: "OpenAI API Key not found"**
- Ensure you have entered your key in the `.env` file correctly.
- Ensure there are no extra spaces around the key.

**Issue: "Module not found"**
- Ensure you have installed all dependencies using `pip install -r requirements.txt`.

**Issue: Topology Validation Errors**
- The LLM may occasionally generate geometrically invalid shapes. If this happens, try generating the section again or refining the description to be more specific.

## Versioning

GeoSIRR uses a stable **release version** and an optional **build identifier**.

- Release version is currently `1.0`.
- If you set the environment variable `GEOSIRR_BUILD`, the displayed version becomes:
   - `1.0+<build>` (PEP 440 *local version* metadata)

This lets you keep the public version at `1.0` while distinguishing different builds (CI runs, git hashes, etc.).

### Examples (Windows PowerShell)

Temporary for the current shell:

```powershell
$env:GEOSIRR_BUILD = "dev.1"
python main.py
```

Using a git short hash (if `git` is available):

```powershell
$env:GEOSIRR_BUILD = (git rev-parse --short HEAD)
python main.py
```

## Acknowledgements

The project was supported by the Center for Integrative Petroleum Research ([CIPR]) at King Fahd University of Petroleum & Minerals (KFUPM) and inspired by [Geo-LM].

## References

- Anikiev, D., Mosquera, J., Ayranci, K., Bott, J., Waheed, U.b. (2026), submitted

[cipr]: https://cpg.kfupm.edu.sa/cipr/
[conda]: https://docs.conda.io/en/latest/
[geo-lm]: https://github.com/williamjsdavis/geo-lm
[llms]: https://en.wikipedia.org/wiki/Large_language_model
[miniforge]: https://github.com/conda-forge/miniforge
[openai]: https://openai.com
[pip]: https://pip.pypa.io/en/stable/
