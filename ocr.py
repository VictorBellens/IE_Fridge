import pytesseract
import os
from PIL import Image
from openai import OpenAI
from datetime import date


key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)


def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='eng')
    return text


def parse_response(response_text):
    # Split the response into entries
    entries = response_text.split(';')
    parsed_entries = []
    for entry in entries:
        if entry.strip():
            parts = entry.split(',')
            item_data = {}
            for part in parts:
                key_value = part.split(':')
                if len(key_value) == 2:
                    item_data[key_value[0].strip()] = key_value[1].strip()
            parsed_entries.append(item_data)
    return parsed_entries


def processed_text(image_path):
    ocr_text = extract_text_from_image(image_path)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Please provide the product names, quantities, and estimated expiration dates from the "
                               "receipt text. Format each entry as follows: 'item: <name>, quantities: <integer>, "
                               "expiration date: <dd/mm/yy>'. Separate each entry with a semicolon. If you do not know"
                               "the expiration date, estimate it, otherwise put 0 if not applicable. The current date"
                               f"is: {date.today()}"
                },
                {
                    "role": "user",
                    "content": ocr_text
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


