import sys
import requests
import json
print("AI WORKER ÇALIŞTI")

def run_ai(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model":"llama3","prompt":prompt},
        stream=True
    )

    full_text = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            full_text += data.get("response","")

    return full_text

if __name__ == "__main__":
    #GUI'de gelen uzun metni stdin'den alıyoruz
    prompt = sys.stdin.buffer.read().decode("utf-8",errors="ignore").strip()

    if not prompt:
        print("AI: Boş veri aldım,yorum yapamıyorum.")
        sys.exit(0)

    result = run_ai(prompt)
    print(result)