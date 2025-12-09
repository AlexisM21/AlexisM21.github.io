from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import pandas as pd
import requests
from parser import match_open_classes
from pypdf import PdfReader
import time
from pathlib import Path
import cache

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

    prompt_text = """
    You are parsing a Titan Degree Audit (TDA).

    Your ONLY task is to extract a STRICT JSON list of all courses the student is allowed to take next.

    ===========================================================
    EXPECTED OUTPUT FORMAT (STRICT JSON ONLY)
    ===========================================================

    {
      "courses_allowed": [
        "SUBJECT NUMBER",
        "SUBJECT NUMBER"
      ]
    }

    No text, no explanation, no markdown.

    ===========================================================
    RULES FOR EXTRACTING COURSES_ALLOWED
    ===========================================================

    1. Extract ONLY courses the student is eligible to take next.
      These appear inside requirement blocks as needed or optional courses.

    2. You MUST exclude:
      - completed courses,
      - in-progress courses,
      - courses belonging to requirement blocks that are already satisfied.

    ===========================================================
    HOW TO IDENTIFY COMPLETED COURSES
    ===========================================================

    A course is COMPLETED if:
    - It appears with a term (FA20, SP23, SS21, etc.),
    AND
    - It displays a final grade (A, A-, B, B+, C, CR, P, etc.).

    Exclude ALL completed courses.

    ===========================================================
    HOW TO IDENTIFY IN-PROGRESS COURSES (IMPORTANT)
    ===========================================================

    A course is IN-PROGRESS if ANY of the following are true:

    1. It appears with a term but **no final grade**.
    2. It is listed under an “In Progress” section of the audit.
    3. It has units assigned but the grade field is blank.
    4. It shows an “IP” label or equivalent.
    5. It appears anywhere else in the audit without a grade, 
      even if the requirement block still lists it as “TAKE ⇒ COURSE”.

    If ANY appearance of a course indicates in-progress status,
    you MUST exclude it from courses_allowed.

    ===========================================================
    HOW TO IDENTIFY SATISFIED REQUIREMENTS
    ===========================================================

    A requirement block is considered SATISFIED if ANY of the following are true:

    1. The block is marked "OK", "MET", or similar.
    2. The student has already completed a course that fulfills that requirement.
    3. The audit shows the requirement as fulfilled using a different course.
    4. A course inside the block appears with a completed grade.

    If a requirement block is satisfied, do NOT include ANY of the courses listed in that block.

    ===========================================================
    HOW TO IDENTIFY VALID COURSE CODES
    ===========================================================

    A course code must follow this format exactly:

        SUBJECT NUMBER

    Examples:
        CPSC 335
        ENGL 103
        MATH 150A

    Include ALL explicit course codes listed under unsatisfied requirement blocks, including:
    - “TAKE ⇒ …”
    - “Course A or Course B”  → include BOTH
    - Lists of electives, major courses, GE courses, etc.

    ===========================================================
    STRICT CONSTRAINTS
    ===========================================================

    - Do NOT include completed courses.
    - Do NOT include in-progress courses.
    - Do NOT include courses from satisfied requirement blocks.
    - Do NOT hallucinate or invent any course codes.
    - Remove duplicates.
    - Output ONLY the JSON object defined above.

    ===========================================================
    YOUR FINAL OUTPUT MUST BE EXACTLY:

    {
      "courses_allowed": [...]
    }

    NO other text is permitted.
    ===========================================================

    """

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
    output_path = Path(__file__).parent / "debug_output.json"
    
    end = time.time()
    print(f"OpenAI response time: {end - start:.2f} seconds")
    return parsed_json

  except Exception as e:
    return {"status" : "error", "errors": [str(e)]}
  


def match_open_classes(courses_allowed):
    """
    Compare courses_allowed[] against OPEN_CACHE and return
    all open sections the student is eligible to take.
    """

    open_data = cache.OPEN_CACHE["data"]  # list of open class dicts
    eligible = []

    allowed_set = set(courses_allowed or [])

    for section in open_data:
        if not isinstance(section, dict):
            continue

        course_id = section.get("course_id", "").strip()

        if course_id in allowed_set:
            eligible.append(section)

    return {
        "eligible_classes": eligible,
        "total_classes": len(eligible)
    }


  
def open_class_connection(file_bytes: bytes, filename: str): 
  audit = parse_tda(file_bytes, filename)
  if "status" in audit and audit["status"] == "error":
    return audit
  courses_allowed = match_open_classes(audit.get("courses_allowed", []))
  return courses_allowed





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





