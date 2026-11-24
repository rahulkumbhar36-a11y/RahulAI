from google import genai
from memory import save_memory, get_memory
import os
import time
import random

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY set nahi hai.")

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.7-flash"


def generate_with_retry(contents):
    for attempt in range(3):
        try:
            return client.models.generate_content(
                model=MODEL,
                contents=contents
            )
        except Exception as e:
            error_text = str(e)

            temporary = any(x in error_text for x in [
                "503", "429", "UNAVAILABLE",
                "RESOURCE_EXHAUSTED", "500", "502", "504"
            ])

            if not temporary or attempt == 2:
                raise

            time.sleep((2 ** attempt) + random.uniform(0, 1))


def get_answer(message):
    message = message.strip()
    lower = message.lower().strip(" ?!.")

    if lower in [
        "tumhara naam kya hai",
        "aapka naam kya hai",
        "what is your name",
        "who are you"
    ]:
        return "Mera naam Rahul AI hai. Main tumhara AI assistant hoon."

    if lower in [
        "mera naam kya hai",
        "what is my name"
    ]:
        name = get_memory("name")
        return f"Tumhara naam {name} hai." if name else "Mujhe abhi tumhara naam yaad nahi hai."

    if lower.startswith("mera naam "):
        name = message[len("mera naam "):].strip()

        if name.lower().endswith(" hai"):
            name = name[:-4].strip()

        if name:
            save_memory("name", name)
            return f"Theek hai dost, main yaad rakhunga ki tumhara naam {name} hai."

    try:
        prompt = f"""
Tum Rahul AI ho.
Tum friendly AI assistant ho.
Hindi aur Hinglish mein simple jawab do.

User message:
{message}
"""

        response = generate_with_retry(prompt)

        if response and response.text:
            return response.text

        return "Dost, AI ne koi answer nahi diya."

    except Exception as e:
        print("Gemini Error:", e)
        return f"AI Error: {str(e)}"


def image_answer(message, image_bytes, mime_type):
    try:
        prompt = f"""
Tum Rahul AI ho.
User ki photo ko samajhkar Hindi/Hinglish mein jawab do.

Question:
{message if message else "Is photo ko describe karo."}
"""

        contents = [
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_bytes
                }
            },
            prompt
        ]

        response = generate_with_retry(contents)

        if response and response.text:
            return response.text

        return "Photo ka answer nahi mil saka."

    except Exception as e:
        print("Image Error:", e)
        return f"Image AI Error: {str(e)}"
