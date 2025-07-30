from src.text_preprocessing import TextPreprocessor
from src.readability import get_readability_scores
from src.style_transform import StyleTransformer
from src.create_diagram import create_diagram
from pathlib import Path
import json
import chardet  # add at the top


def run_pipeline(input_path, model_name="local-model", lang="en"):


    # Detect encoding
    raw_bytes = Path(input_path).read_bytes()
    detected = chardet.detect(raw_bytes)
    encoding = detected["encoding"] or "utf-8"

    try:
        text = raw_bytes.decode(encoding)
    except UnicodeDecodeError:
        text = raw_bytes.decode("utf-8", errors="replace")  # last-resort fallback

    # Step 1: Preprocessing with LanguageTool or Zemberek based on language
    transformer = StyleTransformer(model_name=model_name, lang=lang)
    pre = TextPreprocessor(lang=lang, llm=transformer)

    corrected_text, corrections = pre.correct_text(text)

    # If corrections exist, save them as JSON and print them
    if corrections:
        base = Path(input_path).stem
        out_dir = Path("data/outputs")
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / f"{base}_corrections.json", "w", encoding="utf-8") as f:
            json.dump(corrections, f, indent=2, ensure_ascii=False)

        # Print corrections - adapt print format for Turkish if needed
        for corr in corrections:
            if lang == "en":
                print(f"[Correction] {corr['original']} → {corr['corrected']} ({corr.get('num_issues', '?')} issues)")
            elif lang == "tr":
                # For Turkish, corrections have 'sentence' key and no 'num_issues'
                print(f"[Correction] {corr['original']} → {corr['corrected']} (in sentence: {corr.get('sentence', '')})")

    print(f'{corrected_text}')

    corrected_file = out_dir / f"{base}_corrected.txt"
    corrected_file.write_text(corrected_text, encoding="utf-8")
    print(f"[Saved] Corrected version: {corrected_file}")

    # Step 2: Style transformation (passing lang to StyleTransformer)
    #transformer = StyleTransformer(model_name=model_name, lang=lang)
    outputs = {
        "academic": transformer.transform(corrected_text, "academic"),
        "simple": transformer.transform(corrected_text, "simple"),
        "children": transformer.transform(corrected_text, "child-friendly")
    }

    # Step 3: Readability analysis
    scores = {k: get_readability_scores(v) for k, v in outputs.items()}

    # Save output files
    base = Path(input_path).stem
    out_dir = Path("data/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    for style, content in outputs.items():
        out_file = out_dir / f"{base}_{style}.txt"
        out_file.write_text(content, encoding="utf-8")

    with open(out_dir / f"{base}_readability.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)


    # Step 4: Generate process diagram
    create_diagram(input_path)


    return outputs, scores
