# Natural Language Workflow Examples

Here are examples of describing agent workflows in plain English that can be converted to URFN registry entries.

## Example 1: Content Summarizer

```
Create a workflow called "Article Summarizer" that takes an article URL as input.
First, fetch the article content from the URL.
Then, extract the main text removing any ads or navigation elements.
Next, analyze the article to identify key points and themes.
After that, generate a concise summary of around 3-5 sentences.
Finally, output the summary along with the top 3 key points.
```

## Example 2: Customer Support Assistant

```
I need a "Support Assistant" workflow that takes customer questions about our product.
First, classify whether the question is about technical issues, billing, or general inquiries.
For technical questions, search our knowledge base for relevant articles.
For billing questions, extract any account identifiers mentioned and retrieve account information.
If it's a general inquiry, look up product information from our catalog.
Then, generate a helpful response combining the retrieved information with a friendly, professional tone.
The workflow should output the response text and suggest related resources the customer might need.
```

## Example 3: Research Assistant

```
Build a "Research Helper" workflow that accepts a research topic and desired depth.
Begin by searching for recent academic papers on the topic.
Then, find relevant statistics and data points from reliable sources.
After that, identify key experts and their perspectives on the topic.
Next, organize the information into a structured outline.
Then, generate a comprehensive research brief based on the outline.
Include citations and references for all sources used.
The final output should include the research brief, key findings, and a bibliography.
```

## Example 4: Social Media Content Creator

```
Create a "Social Content" workflow that takes a product name and target audience.
First, gather key product features and benefits from our product database.
Then, research trending topics and hashtags related to the product category.
Next, analyze the target audience demographics and preferences.
Based on that, generate 3 different social media post ideas for each platform (Twitter, Instagram, LinkedIn).
Then, craft the actual post content including suggested images, hashtags, and call-to-action.
Finally, output the complete social media content package with posting recommendations.
```

## Example 5: Email Response Generator

```
I want an "Email Assistant" workflow that takes an incoming email text and creates a response.
First, analyze the email to understand the sender's intent and key questions.
Extract any specific requests or action items mentioned in the email.
Check our knowledge base for information needed to address these requests.
Draft a professional email response that addresses all points raised by the sender.
Make sure to include appropriate greeting and sign-off based on our relationship with the sender.
The workflow should output the complete email response ready to send.
```

## Example 6: Data Analysis Workflow

```
Create a "Data Insights" workflow that takes a CSV file containing sales data.
First, clean the data by removing duplicates and handling missing values.
Then, perform basic statistical analysis to find trends and patterns.
Next, create visualizations showing sales over time and by product category.
After that, identify the top-performing products and underperforming regions.
Generate recommendations based on the analysis findings.
Finally, output a comprehensive report with the analysis, visualizations, and recommendations.
```

## Example 7: Product Recommendation Engine

```
Build a "Recommendation Engine" workflow that takes a user's purchase history and preferences.
Start by analyzing the user's past purchases to identify product categories they like.
Then, find similar products that match their preferences but they haven't purchased yet.
Next, check current promotions and deals that might be relevant to them.
After that, rank the potential recommendations based on likelihood of interest.
Finally, output a personalized list of product recommendations with reasons for each suggestion.
```

## Example 8: Meeting Summarizer

```
Create a "Meeting Notes" workflow that takes a meeting transcript as input.
First, identify all participants mentioned in the transcript.
Then, extract the main discussion topics covered in the meeting.
Next, identify action items and who they were assigned to.
Also, capture any decisions that were made during the meeting.
After that, generate a concise summary of the meeting discussions.
The workflow should output structured meeting notes with summary, attendees, decisions, and action items.
```

## Using the Converter

To convert any of these examples to URFN registry entries:

```python
from nl_to_urfn import convert_natural_language_to_urfn

# Load your natural language description
description = """
Create a workflow called "Article Summarizer" that takes an article URL as input.
First, fetch the article content from the URL.
Then, extract the main text removing any ads or navigation elements.
Next, analyze the article to identify key points and themes.
After that, generate a concise summary of around 3-5 sentences.
Finally, output the summary along with the top 3 key points.
"""

# Convert to URFN registry entries
urfn_registry = convert_natural_language_to_urfn(description)

# Print or save the result
import json
print(json.dumps(urfn_registry, indent=2))



1. Natural Language Workflow Converter
The core component is a natural language processor that converts plain English descriptions into structured workflow definitions:
bashCopy# Example usage
python naturalLanguageAgents.py --description "Create a workflow called Customer Support that takes a customer question as input. First, analyze the sentiment. Then, search for relevant knowledge base articles. Finally, generate a helpful response."
2. Key Features

Plain English Input: Describe workflows in natural language without any special syntax
LLM-Powered Parsing: Uses an LLM to extract workflow structure from natural descriptions
Automatic Structure Detection: Identifies inputs, steps, and outputs automatically
Fallback Parsing: Includes regex-based backup parsing for offline usage
URFN Generation: Converts parsed workflows to URFN registry entries

3. How It Works

Input: You provide a natural language description of your workflow
Parsing: The system extracts:

Workflow name
Input variables
Processing steps
Step connections
Output definition


Conversion: The parsed workflow is converted to URFN registry entries
Registration: The entries can be added to the agent API registry

4. Command-Line Interface
The CLI tool offers multiple ways to use the converter:

File input: --file workflow.txt
Direct input: --description "Create a workflow..."
Interactive mode: --interactive
Output options: Save to file, update existing registry, pretty-print
Visualization: Generate a simple text visualization of the workflow

# Register with the Agent API
from agent_integration_api import agent_api
for urfn_name, urfn_def in urfn_registry.items():
    agent_api.urfn_registry[urfn_name] = urfn_def
```
