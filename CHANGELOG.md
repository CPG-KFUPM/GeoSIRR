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

### Changed

- Model selection, description validation, generation, refinement, and question-answering now thread the selected backend (OpenAI or Ollama) through all LLM calls instead of assuming OpenAI.

## [1.0.0] - 2025-12-30

### Added

- Initial implementation of geological cross-section generation from textual descriptions using OpenAI's LLMs.
- Command-line interface (CLI) for user interaction.
- Validation of geological descriptions and generated outputs.
- Visualization of geological cross-sections using Matplotlib.
- Refinement of existing sections based on user instructions.
- Question-answering feature related to generated sections.
