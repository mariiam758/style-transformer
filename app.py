# app.py
import streamlit as st
from src.pipeline import run_pipeline
from pathlib import Path
import streamlit.components.v1 as components
import json
from charset_normalizer import from_bytes

st.set_page_config(page_title="📝 Text Style Transformer", layout="wide")

st.title("📝 Text Processing Pipeline with Style Transformation")
st.markdown("""
Upload a text file, select a language and model, and run the pipeline.
The app will correct grammar, transform styles, calculate readability, and show a diagram.
""")

# File uploader
uploaded_file = st.file_uploader("📄 Upload a text file (.txt)", type=["txt"])

# Model selection (add/remove models as needed)
model_options = [
    "LM Studio: mistralai/mistral-7b-instruct-v0.3",
    "LM Studio: TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
    "LM Studio: lmstudio-community/gemma-2-2b-it-GGUF",
    "LM Studio: TheBloke/phi-2-GGUF",
    "prithivida/parrot_paraphraser_on_T5"
]
model_choice = st.selectbox("🤖 Select Model", model_options)

# Language selection
lang_choice = st.radio("🌐 Select Language", ["en", "tr"])

if uploaded_file:
    input_path = Path("data/input_texts") / uploaded_file.name
    input_path.parent.mkdir(parents=True, exist_ok=True)

    raw_data = uploaded_file.read()
    results = from_bytes(raw_data)
    best_guess = results.best()

    if best_guess is not None:
        encoding = best_guess.encoding
        file_text = raw_data.decode(encoding, errors='replace')
    else:
        file_text = raw_data.decode('utf-8', errors='replace')

    # Save file as UTF-8
    input_path.write_text(file_text, encoding="utf-8")

    st.success(f"File saved: {input_path}")

    # Full file preview
    st.subheader("📄 Input File Preview")
    st.text_area("Full Input Text", value=file_text, height=300)

    if st.button("🚀 Run Pipeline"):
        with st.spinner("Processing..."):
            outputs, scores = run_pipeline(str(input_path), model_name=model_choice, lang=lang_choice)

        st.success("✅ Pipeline completed successfully!")

        corrections_file = Path("data/outputs") / f"{input_path.stem}_corrections.json"

        if corrections_file.exists():
            with open(corrections_file, "r", encoding="utf-8") as f:
                corrections = json.load(f)

            if corrections:
                total_issues = sum(corr.get("num_issues", 1) for corr in corrections)

                st.subheader(f"🛠️ Corrections Summary — {len(corrections)} sentences, {total_issues} total issues")

                for i, corr in enumerate(corrections, 1):
                    st.markdown(f"**{i}. Issues: {corr.get('num_issues', '?')}**")
                    st.markdown(f"- Original: {corr['original']}")
                    st.markdown(f"- Corrected: {corr['corrected']}")
                    st.markdown("---")
            else:
                st.info("No corrections were found in the text.")
        else:
            st.warning("Corrections JSON not found.")

        # Display transformed outputs
        st.subheader("📄 Transformed Text Outputs")
        for style, content in outputs.items():
            st.markdown(f"### {style.title()} Style")
            st.text_area(f"{style.title()} Output", value=content, height=300)

        # Display readability scores
        st.subheader("📊 Readability Scores")
        for style, score in scores.items():
            st.markdown(f"#### {style.title()} Style")
            for metric, value in score.items():
                try:
                    st.write(f"**{metric}**: {float(value):.2f}")
                except (ValueError, TypeError):
                    st.write(f"**{metric}**: {value}")

        # Display diagram (iframe)
        diagram_path = Path("data/outputs") / f"{input_path.stem}_pipeline_diagram.html"
        if diagram_path.exists():
            st.subheader("🧩 Processing Diagram with Previews")
            components.html(diagram_path.read_text(encoding="utf-8"), height=800, scrolling=True)
        else:
            st.warning("Diagram not found.")
else:
    st.info("Please upload a text file to begin.")
