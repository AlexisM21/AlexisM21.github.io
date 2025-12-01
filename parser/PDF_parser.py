from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import pandas as pd

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)

with open('pdf_testing', 'rb') as f:
    uploaded_file = client.files.create(
    file=f,
    purpose="assistants"
)

file_id = uploaded_file.id    

prompt_text= '''
You are parsing through a university degree audit / credit report.

Extract the information into STRICT JSON following this schema:

{
  "student_info": {
    "name": "string or null",
    "id": "string or null",
    "catalog_year": "string or null"
  },
  "completed_courses": [
    {
      "term": "string or null",
      "subject": "string",
      "number": "string",
      "title": "string or null",
      "units": number,
      "grade": "string or null",
      "status": "string"
    }
  ],
  "requirements": [
    {
      "requirement_id": "string",
      "name": "string",
      "type": "string",
      "total_units_required": number,
      "total_units_completed": number,
      "courses_allowed": ["string", "string"]
    }
  ]
}

Rules:
- ONLY output valid JSON, no explanation, no markdown.
- Always include all top-level keys: "student_info", "completed_courses", "requirements".
- Use null for unknown values instead of removing keys.
- For "status" in completed_courses, use exactly "completed" or "in_progress".
- For "type" in requirements, use one of: "GE", "Major", "Support", "Elective".
- For "courses_allowed", each item should be a course code like "CPSC 131" or exactly as it appears in the document.
- Replace the example types (like number, string) with real JSON values in the final output.
'''

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": prompt_text,
                },
                {
                    "type": "input_file",
                    "file_id": file_id,
                },
            ],
        }
    ],
)

raw_text = response.output[0].content[0].text

output_path = "parsed_credits.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(json.loads(raw_text), f, indent=2, ensure_ascii=False)
