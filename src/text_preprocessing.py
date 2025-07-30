# src/text_preprocessing.py 
import os
import nltk
from nltk.tokenize import sent_tokenize
import subprocess

nltk.download('punkt')

# Ensure JAVA_HOME and PATH are set (adjust to your actual JDK path)
os.environ["JAVA_HOME"] = r"C:\Users\PC_6155__\AppData\Local\Programs\Eclipse Adoptium\jdk-21.0.8.9-hotspot"
os.environ["PATH"] = os.path.join(os.environ["JAVA_HOME"], "bin") + ";" + os.environ["PATH"]


class TextPreprocessor:
    def __init__(self, lang='en', llm=None):
        self.lang = lang.lower()
        self.tool = None  # Safe default
        self.llm = llm  # For Turkish LLM correction

        if self.lang == 'en':
            import language_tool_python
            print("Initializing LanguageTool for English...")
            self.tool = language_tool_python.LanguageTool('en-US')

        elif self.lang == 'tr':
            if self.llm is None:
                raise ValueError("LLM must be provided for Turkish.")
            print("Using LLM for Turkish grammar correction...")

        else:
            raise ValueError(f"Unsupported language: {lang}")

    def correct_text(self, text):
        sentences = sent_tokenize(text)
        corrected_sentences = []
        corrections = []

        if self.lang == 'en':
            for sentence in sentences:
                try:
                    matches = self.tool.check(sentence)
                    corrected_sent = self.tool.correct(sentence)
                    corrected_sentences.append(corrected_sent)
                except Exception as e:
                    print(f"[Warning] Error correcting sentence: '{sentence}' → {e}")
                    corrected_sentences.append(sentence)

            correction_list = [
                {
                    "original": s,
                    "corrected": c,
                    "num_issues": len(self.tool.check(s))
                }
                for s, c in zip(sentences, corrected_sentences)
                if s != c
            ]

            corrected_text = ' '.join(corrected_sentences)
            return corrected_text, correction_list

        elif self.lang == 'tr':
            for sentence in sentences:
                try:
                    corrected_sentence = self.correct_sentence_tr_with_llm(sentence)
                    corrected_sentences.append(corrected_sentence)
                    if sentence != corrected_sentence:
                        corrections.append({
                            "original": sentence,
                            "corrected": corrected_sentence
                        })
                except Exception as e:
                    print(f"[Warning] LLM error on sentence: '{sentence}' → {e}")
                    corrected_sentences.append(sentence)

            corrected_text = ' '.join(corrected_sentences)
            return corrected_text, corrections

    def correct_sentence_tr_with_llm(self, sentence):
        """Use LLM to correct a single Turkish sentence."""
        prompt = (
            f"Aşağıdaki cümlede yazım veya dil bilgisi hatası varsa düzelt:\n"
            f"{sentence}\n"
            f"Sadece düzeltilmiş cümleyi döndür. Eğer hata yoksa cümleyi aynen döndür."
        )
        print(f"[DEBUG] Sending sentence to LLM for correction:\n{sentence}")
        corrected = self.llm.transform(prompt, style="grammar")
        return corrected.strip()

    def __del__(self):
        if self.lang == 'en' and self.tool is not None:
            try:
                self.tool.close()
            except Exception as e:
                print(f"[Warning] Failed to close LanguageTool: {e}")
