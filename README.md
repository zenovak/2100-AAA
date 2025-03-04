Agent of All Agents API - Contribution Guide

Welcome to the Agent of All Agents API repository! This API standard is inspired by the OpenAI API and is designed to be flexible, allowing contributors to add new functionalities using API augmentation and a modular function add-on system. If you’re interested in contributing, this guide will walk you through the process of submitting a pull request (PR) that fits seamlessly into our architecture.

📋 Table of Contents
	1.	API Overview
	2.	Getting Started
	3.	Code Structure
	4.	Writing Compatible PRs
	•	4.1 API Augmentation
	•	4.2 Function Add-Ons
	•	4.3 Unique Reserved Function Names
	5.	Testing Your Contribution
	6.	Submitting a Pull Request
	7.	Code Style Guidelines
	8.	Getting Help

1. API Overview

The Agent of All Agents API is built to:
	•	Be compatible with OpenAI’s API standards.
	•	Support API augmentation to extend core functionalities.
	•	Allow for modular function add-ons using Unique Reserved Function Names (URFNs).
	•	Maintain a flexible and scalable architecture for various AI agents.

2. Getting Started

Prerequisites
	•	Python 3.10+ or a compatible language as per module requirements.
	•	Poetry or pip for dependency management.
	•	An understanding of RESTful API standards and OpenAI API compatibility.

Installation
	1.	Fork and clone the repository:

git clone https://github.com/yourusername/agent-of-all-agents-api.git
cd agent-of-all-agents-api


	2.	Install dependencies:

poetry install  # or pip install -r requirements.txt

3. Code Structure

agent-of-all-agents-api/
├── core/                     # Core API logic and base functions
├── addons/                   # Modular function add-ons
├── docs/                     # API documentation and guides
├── tests/                    # Unit and integration tests
├── urfn_registry.json        # Registry of Unique Reserved Function Names
├── CONTRIBUTING.md           # This file
├── README.md
└── setup.py

4. Writing Compatible PRs

4.1 API Augmentation

API augmentation allows you to add new endpoints or enhance existing ones without disrupting core functionalities.

How to add API augmentations:
	•	Create new endpoint files in the core/ directory.
	•	Use OpenAPI (Swagger) annotations for documentation compatibility.
	•	Ensure your endpoints support JSON request and response formats.

Example:

# core/new_feature.py

from fastapi import APIRouter

router = APIRouter()

@router.post("/v1/augment/new-feature")
async def new_feature(data: dict):
    """
    POST /v1/augment/new-feature
    ---
    description: Adds a new feature to the API
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              input:
                type: string
    responses:
      200:
        description: Success
    """
    # Your implementation here
    return {"message": "Feature added successfully!"}

4.2 Function Add-Ons

Function add-ons allow contributors to create modular functionalities callable by Unique Reserved Function Names (URFNs).

How to add a function add-on:
	•	Create a new Python module in the addons/ directory.
	•	Define your function using the following template:

Example:

# addons/summary_generator.py

def urfn_summarize_text(input_text: str) -> dict:
    """
    URFN: urfn_summarize_text
    Description: Summarizes the input text and returns a concise version.
    Parameters:
        input_text (str): Text to summarize.
    Returns:
        dict: A JSON object with the summarized text.
    """
    # Summarization logic here
    summary = input_text[:100] + "..."  # Placeholder
    return {"summary": summary}

4.3 Unique Reserved Function Names (URFNs)

URFNs are standardized function names to ensure consistent and conflict-free execution of add-ons.

Guidelines for URFNs:
	1.	Must follow the format: urfn_<function_purpose>.
	2.	Register your URFN in urfn_registry.json:

{
  "urfn_summarize_text": {
    "description": "Summarizes input text.",
    "module": "summary_generator",
    "function": "urfn_summarize_text"
  }
}

5. Testing Your Contribution

Testing Requirements:
	•	Place tests in the tests/ directory.
	•	Use pytest for unit and integration tests.
	•	Ensure your tests cover various edge cases and input types.

Example Test:

# tests/test_summary_generator.py

import pytest
from addons.summary_generator import urfn_summarize_text

def test_urfn_summarize_text():
    result = urfn_summarize_text("This is a long text that needs summarizing.")
    assert "summary" in result

Run tests:

pytest

6. Submitting a Pull Request

PR Requirements:
	1.	Ensure all tests pass locally.
	2.	Update urfn_registry.json if adding new functions.
	3.	Write or update API documentation in the docs/ directory.
	4.	Follow the commit message format:

[Feature] Add urfn_summarize_text for text summarization



Creating a PR:
	1.	Push your branch:

git push origin feature/your-feature


	2.	Open a PR to the main branch.
	3.	Provide a clear description and link any related issues.

7. Code Style Guidelines
	•	PEP 8 for Python code.
	•	RESTful standards for API endpoints.
	•	Type hints for function signatures.

Linting:

flake8

8. Getting Help

For questions, open a discussion or reach out via issues.

Happy coding! 🚀
