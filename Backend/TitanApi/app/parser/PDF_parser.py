from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import pandas as pd
import requests
from parser import match_open_classes
from pypdf import PdfReader
import time

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)


def parse_tda(file_bytes: bytes, filename: str):
  try: 

    start = time.time()

    uploaded_file = client.files.create(
      file=(filename, file_bytes),
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
          "in_progress": "string"
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
    - Replace any example types (like "string", "number") with actual JSON values in the final output.
    - If the class is "in_progress" do not add it to the "courses_allowed" list.
    - Do not invent or hallucinate courses, requirements, or values that are not supported by the text.

    Additional parsing rules:
    - This is a Titan Degree Audit (TDA) or similar university degree audit.
    - IGNORE all requirement status labels such as "NO", "OK", "YES", and similar labels at the top of sections. These are NOT classes and should never appear in the JSON.
    - IGNORE section headers, legends, comments, arrows, and hints such as:
      - ">>>IMPORTANT INFORMATION<<<", "LEGEND", "GENERAL EDUCATION PROGRAM", etc.
      - "TAKE==>", ">>", ">>> Waived for this major <<", and similar advisory lines.
    - ONLY treat a line as a course when it has a recognizable pattern with:
      - a term (e.g., "FA20", "SP25", "SS21"),
      - a subject (e.g., "CPSC", "MATH", "PHYS", "ENGL"),
      - a course identifier/number (e.g., "120A", "131", "225L"),
      - and usually credits, grade, and title on the same or following text.
    - Lines like "NO COMPUTER SCIENCE CORE COURSES", "OK GE UNITS", or "AMERICAN GOVERNMENT (3 UNITS
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
    print("SUCCESS RESPONSE CLINET")
    raw_text = response.output[0].content[0].text

    parsed_json = json.loads(raw_text)

    end = time.time()
    print(f"OpenAI response time: {end - start:.2f} seconds")
    return parsed_json

  except Exception as e:
    return {"status" : "error", "errors": [str(e)]}
  

  
def open_class_connection(file_bytes: bytes, filename: str): 
  audit = parse_tda(file_bytes, filename)
  if "status" in audit and audit["status"] == "error":
    return audit
  open_list = match_open_classes.get_open_class_user(audit)
  return open_list





# from dotenv import load_dotenv
# import os
# from openai import OpenAI
# import json
# import pandas as pd
# import requests
# from parser import match_open_classes
# from pypdf import PdfReader
# import io
# import time

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

# if not api_key:
#     raise RuntimeError("OPENAI_API_KEY not found in .env")

# client = OpenAI(api_key=api_key)


# def extract_pdf_text(file_bytes: bytes) -> str:
#     """Extract text locally — much faster than uploading the whole PDF."""
#     reader = PdfReader(io.BytesIO(file_bytes))
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() or ""
#     return text


# def parse_tda(file_bytes: bytes, filename: str):
#     try:
#         print("IN TDA PARSER (FAST MODE)")
#         start = time.time()
#         # ⭐ FAST: Extract PDF text locally
#         extracted_text = extract_pdf_text(file_bytes)

#         # ⭐ Short + optimized prompt
#         prompt = f"""
#         You will parse a Titan Degree Audit.

#         Extract JSON ONLY with:
#         - student_info
#         - completed_courses[]
#         - requirements[]

#         IMPORTANT:
#         - No explanation, no markdown.
#         - Null for unknown.
#         - status = completed | in_progress
#         - type = GE | Major | Support | Elective
#         - Don’t hallucinate anything.
        
#         RAW TDA TEXT:
#         {extracted_text}
#         """

#         # ⭐ Faster model
#         response = client.responses.create(
#             model="gpt-4.1",
#             input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
#         )

#         raw_text = response.output[0].content[0].text
#         end = time.time()
#         # ⭐ Parse JSON output
#         print(f"OpenAI response time: {end - start:.2f} seconds")
#         return json.loads(raw_text)

#     except Exception as e:
#         print("ERROR IN TDA PARSER:", e)
#         return {"status": "error", "errors": [str(e)]}

# def open_class_connection(file_bytes: bytes, filename: str): 
#   audit = parse_tda(file_bytes, filename)
#   if "status" in audit and audit["status"] == "error":
#     return audit
#   open_list = match_open_classes.get_open_class_user(audit)
#   return open_list





