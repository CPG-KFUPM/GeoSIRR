# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Support for [Ollama](https://ollama.com) as a local LLM provider, alongside OpenAI.
- Interactive LLM provider selection (OpenAI or Ollama) at application startup.
- Automatic Ollama server health check and local model discovery.
- Documentation for Ollama installation, configuration, and troubleshooting in the README.
- `get_ollama_models()` parses the `ollama.list()` response object, showing locally installed Ollama models.
- Per-run log files with start/end timestamps, status, and runtime for each generation stage and the complete workflow.
- `plot_section.py` for creating a PNG directly from a GeoSIRR cross-section text file.
- `examples/plot_examples.py` for regenerating all valid text examples with shared or per-example settings.
- Plot CLI controls for titles, model and legend padding, legend gap, line width, vertex size, vertex-label size, legend font size, figure size, and title spacing.

### Changed

- Model selection, description validation, generation, refinement, and question-answering now thread the selected backend (OpenAI or Ollama) through all LLM calls instead of assuming OpenAI.
- Cross-section plots are saved to PNG before being displayed interactively, instead of after.
- Stage and total workflow runtimes are now shown in the console during generation.
- Updated the list of available OpenAI models and changed the sorting order to prioritize the latest models first.
- Plot padding now scales independently with the horizontal and vertical model ranges, and space can be reserved beside the model for the legend.

### Fixed

- Replaced the removed `matplotlib.cm.get_cmap()` call with `matplotlib.pyplot.colormaps[...]`, fixing an `AttributeError: module 'matplotlib.cm' has no attribute 'get_cmap'` when plotting cross sections on recent Matplotlib versions.
- Vertex markers on model boundaries are no longer clipped when plot padding is zero.

## [1.0.0] - 2025-12-30

### Added

- Initial implementation of geological cross-section generation from textual descriptions using OpenAI's LLMs.
- Command-line interface (CLI) for user interaction.
- Validation of geological descriptions and generated outputs.
- Visualization of geological cross-sections using Matplotlib.
- Refinement of existing sections based on user instructions.
- Question-answering feature related to generated sections.
