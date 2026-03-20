from crewai import LLM
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

def generate_title(prompt: str):
    try:
        lang = detect(prompt)
    except:
        lang = "en"
    if lang == "id":
        instruction = (
            "Buat judul singkat, jelas, kreatif, dan relevan dengan konteks hukum "
            "berdasarkan prompt berikut dalam bahasa Indonesia."
        )
    else:
        instruction = (
            "Generate a short, clear, creative, and legally-relevant title based on this prompt in English."
        )

    llm = LLM(model="gpt-3.5-turbo", temperature=0.7)

    llm_prompt = f"{instruction}\n\nUser prompt: '{prompt}'"

    generated_title = llm.call(llm_prompt)
    return generated_title