import argparse
from src.pipeline import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run style transformation pipeline.")
    parser.add_argument("input_path", type=str, help="Path to input text file")
    parser.add_argument("--model", type=str, default="local-model", help="Model name for LM Studio or HuggingFace")
    parser.add_argument("--lang", type=str, default="en", help="Language code: 'en' or 'tr'")

    args = parser.parse_args()
    outputs, scores = run_pipeline(args.input_path, model_name=args.model , lang=args.lang)

    print("\nTransformation completed. Readability scores:")
    for style, score in scores.items():
        print(f"\n{style.capitalize()} Style:")
        for metric, value in score.items():
            print(f"  {metric}: {value}")



# TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF

# python main.py data/input_texts/example.txt --model "LM Studio: TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF" --lang en

# python main.py data/input_texts/makale.txt --model "LM Studio: TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF" --lang tr


# lmstudio-community/gemma-2-2b-it-GGUF

# python main.py data/input_texts/example.txt --model "LM Studio: lmstudio-community/gemma-2-2b-it-GGUF" --lang en

# python main.py data/input_texts/makale.txt --model "LM Studio: lmstudio-community/gemma-2-2b-it-GGUF" --lang tr

# python main.py data/input_texts/makale_2.txt --model "LM Studio: lmstudio-community/gemma-2-2b-it-GGUF" --lang tr


# TheBloke/phi-2-GGUF

# python main.py data/input_texts/example.txt --model "LM Studio: TheBloke/phi-2-GGUF" --lang en

# python main.py data/input_texts/makale.txt --model "LM Studio: TheBloke/phi-2-GGUF" --lang tr

