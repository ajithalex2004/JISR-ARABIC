import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

with open('scratch/missing_gr6_words.json', encoding='utf-8') as f:
    missing_items = json.load(f)

# unique clean words
clean_words = sorted(list(set([m[1] for m in missing_items if m[1]])))
print(f"Total clean words to translate: {len(clean_words)}")

# Batch in chunks of 50
chunk_size = 50
dict_results = {}

for i in range(0, len(clean_words), chunk_size):
    chunk = clean_words[i:i + chunk_size]
    prompt = f"""
You are an expert Arabic-English lexicographer specializing in the UAE Ministry of Education Grade 6 curriculum.
Given the following list of Arabic words from Grade 6 (Chapter: احتياجاتي ورغباتي - My Needs & Desires, and buying & selling):
{json.dumps(chunk, ensure_ascii=False)}

Return a JSON object where each key is the exact Arabic word from the input list, and the value is:
{{
  "translation": "Concise English translation (e.g. desire / wish, essential / necessary)",
  "partOfSpeech": "noun" | "verb" | "adjective" | "particle" | "pronoun" | "adverb",
  "root": "Arabic root in format X-Y-Z if applicable, or omit if none"
}}

Respond ONLY with valid JSON.
"""
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        batch_res = json.loads(response.text)
        dict_results.update(batch_res)
        print(f"Processed chunk {i // chunk_size + 1} ({len(dict_results)}/{len(clean_words)})", flush=True)
    except Exception as e:
        print(f"Error in chunk {i}: {e}", flush=True)

with open('scratch/gr6_generated_dict.json', 'w', encoding='utf-8') as f:
    json.dump(dict_results, f, ensure_ascii=False, indent=2)

print(f"Successfully generated {len(dict_results)} dictionary entries!", flush=True)
