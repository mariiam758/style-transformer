import requests
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize


# Model context length lookup table
MODEL_CONTEXT_LIMITS = {
    "mistral-7b": 4096,
    "llama-3-8b": 8192,
    "llama-3-70b": 8192,
    "mixtral-8x7b": 8192,
    "gpt-3.5": 4096,
    "gpt-4": 128000,
    "claude-3-opus": 200000,
    "command-r": 32768,
    "phi-2": 2048,
    "gemma-7b": 8192,
}

def get_model_context_length(model_name):
    model_name = model_name.lower()
    for key in MODEL_CONTEXT_LIMITS:
        if key in model_name:
            return MODEL_CONTEXT_LIMITS[key]
    return 4096  # default

class StyleTransformer:
    def __init__(self, mode="lm_studio", model_name="local-model", lang="en"):
        self.mode = mode
        self.model_name = model_name
        self.lang = lang.lower()

        context_tokens = get_model_context_length(self.model_name)
        self.context_tokens = context_tokens
        self.chars_per_token = 3
        self.window_size = context_tokens * self.chars_per_token
        self.overlap_ratio = 0.2
        self.overlap_chars = int(self.window_size * self.overlap_ratio)
        print(f"[DEBUG] Model: {self.model_name}, context_tokens={context_tokens}, window_size={self.window_size}, overlap_chars={self.overlap_chars}")

        if model_name.startswith("LM Studio:"):
            self.mode = "lm_studio"
            self.model_name = model_name.replace("LM Studio:", "").strip()
        elif "/" in model_name and mode != "hf":
            self.mode = "lm_studio"

        if self.mode == "hf":
            print("[DEBUG] Initializing HuggingFace model...")
            self.hf_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.hf_model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.hf_model.eval()

    def build_prompt(self, text, style):
        if self.lang == "en":
            return f"Rewrite the following text in {style} style:\n{text}\nReturn only the edited version."
        elif self.lang == "tr":
            return f"Aşağıdaki metni {style} tarzında yeniden yaz:\n{text}\nSadece düzenlenmiş metni döndür."
        else:
            return f"Rewrite the following text in {style} style:\n{text}\nReturn only the edited version."

    def transform(self, text, style="academic"):
        print(f"[DEBUG] Starting sliding window transformation for style '{style}'...")
        chunks = self.split_with_overlap(text, self.window_size, self.overlap_chars)
        transformed_chunks = []

        for idx, chunk in enumerate(chunks):
            print(f"[DEBUG] Processing chunk {idx+1}/{len(chunks)}...")
            prompt = self.build_prompt(chunk, style)
            if self.mode == "lm_studio":
                result = self._lm_studio_transform(prompt, style)
            elif "hf" in self.mode or "/" in self.model_name:
                result = self._hf_transform(prompt)
            else:
                raise NotImplementedError("Unknown mode.")
            transformed_chunks.append(result)

        final_text = self.merge_chunks(transformed_chunks)
        return final_text

    def _lm_studio_transform(self, prompt, style):
        url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 512
        }

        try:
            print(f"[DEBUG] Sending prompt to LM Studio for style '{style}'...")
            response = requests.post(url, headers=headers, json=payload)
            print("[DEBUG] Response received from LM Studio.")
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[ERROR] LM Studio Error: {e}")
            return "Error during transformation."

    def _hf_transform(self, prompt):
        inputs = self.hf_tokenizer(prompt, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.hf_model.generate(**inputs, max_new_tokens=200)
        output_text = self.hf_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return output_text

    def split_with_overlap(self, text, window_size, overlap_chars):
        step = window_size - overlap_chars
        chunks = [text[i:i+window_size] for i in range(0, len(text), step)]
        print(f"[DEBUG] Split text into {len(chunks)} chunks (window={window_size}, overlap={overlap_chars})")
        return chunks


    def merge_chunks(self, chunks):
        print("[DEBUG] Merging chunks using sentence-aware logic...")

        merged_sentences = []
        seen_sentences = set()

        # Select tokenizer language
        lang = self.lang if hasattr(self, 'lang') else 'en'  # fallback
        tokenizer_lang = 'turkish' if lang == 'tr' else 'english'

        for idx, chunk in enumerate(chunks):
            sentences = sent_tokenize(chunk, language=tokenizer_lang)
            new_sentences = []

            for sent in sentences:
                cleaned_sent = sent.strip()
                if cleaned_sent and cleaned_sent not in seen_sentences:
                    new_sentences.append(cleaned_sent)
                    seen_sentences.add(cleaned_sent)

            print(f"[DEBUG] Chunk {idx+1}: {len(new_sentences)} new sentences added.")
            merged_sentences.extend(new_sentences)

        final_text = " ".join(merged_sentences)
        print(f"[DEBUG] Final merged text length: {len(final_text)} characters.")
        return final_text

