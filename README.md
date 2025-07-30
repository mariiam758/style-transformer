# Text Processing Pipeline with Style Transformation

This project provides an interactive Streamlit web application for processing text files. It performs grammar correction, style transformation, readability analysis, and visualizes the processing pipeline.

## Features

- Upload plain text files for processing.
- Grammar correction using LanguageTool (English) or llm model (Turkish).
- Style transformations into academic, simple, and child-friendly styles using large language models.
- Readability scoring (e.g., Flesch Reading Ease).
- Interactive visualization of the entire pipeline with content previews.
- Downloadable correction logs in JSON format.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Java 17 or higher installed and configured in your environment (required for LanguageTool).

### How to run

1. Install the dependencies:

```bash

pip install -r requirements.txt
```

2. Run the Streamlit app:

```bash

streamlit run app.py
```

3. Open your browser and go to the URL shown in the terminal (usually http://localhost:8501).


### Usage

- Upload a .txt file.
- Select the desired language (en or tr).
- Choose a language model from the dropdown.
- Click "Run Pipeline" to process.
- View the input preview, corrections, transformed styles, readability scores, and the pipeline visualization.


### Notes

- LanguageTool requires Java 17 or later. Make sure Java is installed and added to your system's PATH.
- The style transformation relies on LLMs, which may require internet or local model access depending on your setup.


### Project Structure

app.py: Streamlit application entry point.

src/pipeline.py: Main pipeline execution.

src/text_preprocessing.py: Grammar correction utilities.

src/style_transform.py: Style transformation logic.

src/create_diagram.py: Pipeline visualization with Plotly.

data/input_texts/: Folder to store uploaded text files.

data/outputs/: Folder to store output files (corrected texts, JSONs, diagrams).