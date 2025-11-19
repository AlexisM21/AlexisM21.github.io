import time
import csv
import os
import re
from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
)

# ---------- CONFIG ----------
CLASS_SEARCH_URL = (
    "https://cmsweb.fullerton.edu/psc/CFULPRD/EMPLOYEE/SA/c/"
    "SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?&public"
)

SUBJECT_VISIBLE_TEXT = "Computer Science"
OUTPUT_CSV = "csuf_cpsc_all_terms_sections.csv"
UPLOAD_URL = "http://127.0.0.1:8000/open/upload"

# Day mapping for your schema
DAY_MAP = {"M": 1, "T": 2, "W": 3, "R": 4, "F": 5, "S": 6, "U": 7}
# ----------------------------


def init_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 900)
    return driver


def get_term_dropdown(driver):
    wait = WebDriverWait(driver, 30)
    return wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//select[contains(@id, 'STRM') or contains(@id, 'TERM')]")
        )
    )


def get_subject_dropdown(driver):
    wait = WebDriverWait(driver, 30)
    return wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//select[contains(@id, 'SUBJECT') or contains(@id, 'SUBJECT$0')]")
        )
    )


def get_all_terms(driver):
    term_select_el = get_term_dropdown(driver)
    sel = Select(term_select_el)
    terms = []
    for opt in sel.options:
        text = opt.text.strip()
        value = opt.get_attribute("value")
        if not text or "select" in text.lower():
            continue
        terms.append({"value": value, "text": text})
    return terms


def fill_search_form_for_term(driver, term_text):
    """
    Choose term + Computer Science, handle the 'over 50 classes' popup,
    land on results page.
    """
    wait = WebDriverWait(driver, 30)

    print(f"    → Setting TERM to: {term_text}")
    term_select_el = get_term_dropdown(driver)
    Select(term_select_el).select_by_visible_text(term_text)
    time.sleep(2)

    # SUBJECT = Computer Science
    for attempt in range(3):
        try:
            subject_select_el = get_subject_dropdown(driver)
            sel = Select(subject_select_el)

            chosen_text = None
            for opt in sel.options:
                t = opt.text.strip()
                if "COMPUTER SCIENCE" in t.upper():
                    chosen_text = t
                    break

            if not chosen_text:
                raise Exception("Could not find subject option containing 'Computer Science'")

            sel.select_by_visible_text(chosen_text)
            print(f"    → Selected SUBJECT: {chosen_text}")
            break
        except StaleElementReferenceException:
            if attempt == 2:
                raise
            print("    ↻ Subject dropdown went stale, retrying...")
            time.sleep(1)

    # Click Search
    search_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//input[@type='button' or @type='submit']"
                "[contains(@value,'Search') or contains(@id,'SRCH_BTN')]",
            )
        )
    )
    search_button.click()
    print("    → Clicked Search")

    # Handle "over 50 classes" popup if it appears
    try:
        warning_ok = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[contains(@value,'OK') or contains(@value,'Ok')]")
            )
        )
        print("    → 'Over 50 classes' popup detected → clicking OK")
        warning_ok.click()
        time.sleep(3)
    except TimeoutException:
        pass

    time.sleep(4)


def parse_time_to_minutes(tstr: str):
    tstr = tstr.strip().upper()
    if "TBA" in tstr or "ARR" in tstr:
        return None
    try:
        dt = datetime.strptime(tstr, "%I:%M%p")
        return dt.hour * 60 + dt.minute
    except ValueError:
        return None


def normalize_days_str(days_str: str) -> str:
    """
    Convert 'MoWe' → 'MW', 'TuTh' → 'TR', etc.
    """
    mapping = {
        "Mo": "M",
        "Tu": "T",
        "We": "W",
        "Th": "R",
        "Fr": "F",
        "Sa": "S",
        "Su": "U",
    }
    result = ""
    s = days_str.strip()
    i = 0
    while i < len(s):
        chunk = s[i:i + 2]
        if chunk in mapping:
            result += mapping[chunk]
            i += 2
        else:
            i += 1
    return result


def extract_course_id(text: str) -> str:
    """
    From header text like 'CPSC 120A - Introduction to Programming Lecture'
    pull out 'CPSC 120A'.
    """
    if not text:
        return ""
    upper = text.upper()
    m = re.search(r"CPSC\D*(\d{3}[A-Z]?)", upper)
    if not m:
        return ""
    num = m.group(1)  # e.g. '120A'
    return f"CPSC {num}"


def expand_days_time(
    term_text: str,
    course_id: str,
    crn: str,
    section: str,
    days_time: str,
    room: str,
    instructor: str,
    instruction_mode: str,
):
    """
    Convert 'MoWe 8:30AM - 9:20AM' into multiple rows (one per day).
    """
    rows = []
    if not days_time:
        return rows

    parts = days_time.split()
    # Expected: ['MoWe', '8:30AM', '-', '9:20AM']
    if len(parts) < 4 or parts[2] != "-":
        return rows

    days_raw = parts[0]
    start_str = parts[1]
    end_str = parts[3]

    days_compact = normalize_days_str(days_raw)
    start_min = parse_time_to_minutes(start_str)
    end_min = parse_time_to_minutes(end_str)

    if start_min is None or end_min is None:
        return rows

    for ch in days_compact:
        dnum = DAY_MAP.get(ch.upper())
        if not dnum:
            continue

        rows.append(
            {
                "term": term_text.upper(),
                "course_id": course_id,
                "crn": crn,
                "section": section,
                "day_of_week": dnum,
                "start_min": start_min,
                "end_min": end_min,
                "room": room,
                "instruction_mode": instruction_mode,
                "professor": instructor,
                "status": "Open",  # only open classes are shown
            }
        )

    return rows


def scrape_sections_from_current_page(driver, term_text: str):
    """
    Grab all real section rows (by numeric CRN in first cell),
    then for each one:
      - find nearest header row with CPSC
      - extract course_id
      - expand days into separate rows
    """
    all_rows = []

    section_rows = driver.find_elements(
        By.XPATH,
        "//tr[td[1]//a[normalize-space()!='' and "
        "string-length(normalize-space())>=5 and "
        "translate(normalize-space(),'0123456789','')='']]"
    )

    print(f"  → Found {len(section_rows)} section rows on this page.")

    for row in section_rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 6:
            continue

        crn = cells[0].text.strip()
        if not (crn.isdigit() and len(crn) >= 5):
            continue

        # Clean section number ("01-LEC\nRegular" → "01")
        raw_section = cells[1].text.strip()
        m = re.match(r"(\d+)", raw_section)
        section = m.group(1) if m else raw_section

        days_time = cells[2].text.strip()
        room = cells[3].text.strip()
        instruction_mode_col = cells[4].text.strip()
        instructor = cells[5].text.strip()

        # --- Extract course_id from nearest header row above ---
        course_id = ""
        try:
            header_tr = row.find_element(
                By.XPATH,
                ".//preceding::tr[contains(., 'CPSC')][1]"
            )
            course_id = extract_course_id(header_tr.text)
        except NoSuchElementException:
            pass

        # Fallback: CRN link attributes
        if not course_id:
            try:
                link = cells[0].find_element(By.TAG_NAME, "a")
                candidates = [
                    link.get_attribute("title") or "",
                    link.get_attribute("aria-label") or "",
                    link.text or "",
                ]
                for txt in candidates:
                    cid = extract_course_id(txt)
                    if cid:
                        course_id = cid
                        break
            except Exception:
                pass

        # Infer instruction mode
        if instruction_mode_col:
            instruction_mode = instruction_mode_col.strip()
        else:
            rl = room.lower()
            if "online" in rl or "web" in rl:
                instruction_mode = "Online"
            elif "hybrid" in rl:
                instruction_mode = "Hybrid"
            else:
                instruction_mode = "In Person"

        print(
            f"    ✔ CRN: {crn} | COURSE: {course_id or 'N/A'} | "
            f"SECTION: {section} | INSTR: {instructor or 'N/A'}"
        )

        expanded = expand_days_time(
            term_text, course_id, crn, section, days_time, room, instructor, instruction_mode
        )
        all_rows.extend(expanded)

    return all_rows


def click_next_if_possible(driver) -> bool:
    try:
        next_button = driver.find_element(
            By.XPATH,
            "//*[contains(@id,'NEXT') and (self::a or self::input or self::span)]",
        )
        classes = next_button.get_attribute("class") or ""
        if "PS_INACTIVE" in classes:
            return False
        next_button.click()
        print("  → Clicked Next")
        time.sleep(3)
        return True
    except NoSuchElementException:
        return False


def go_back_to_search_form(driver):
    try:
        btn = driver.find_element(
            By.XPATH,
            "//*[contains(@value,'New Search') or contains(text(),'New Search')]"
        )
        btn.click()
        print("  → Returning to search form...")
        time.sleep(2)
    except NoSuchElementException:
        print("⚠️ New Search button not found.")


def upload_csv(filepath: str):
    print(f"\n🌐 Uploading {filepath} ...")
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f, "text/csv")}
        resp = requests.post(UPLOAD_URL, files=files)
    print(f"→ Upload status: {resp.status_code}")
    try:
        print(resp.text)
    except Exception:
        pass


def main():
    driver = init_driver()

    try:
        driver.get(CLASS_SEARCH_URL)
        print("\n➡ Log in and navigate to the Class Search form.")
        input("Press ENTER when ready... ")

        terms = get_all_terms(driver)

        print("\n📅 Terms found:")
        for t in terms:
            print("  -", t["text"])

        all_rows = []

        for idx, term in enumerate(terms, 1):
            tname = term["text"]
            print("\n==============================")
            print(f"🔎 Term {idx}/{len(terms)}: {tname}")
            print("==============================")

            try:
                get_term_dropdown(driver)
            except Exception:
                go_back_to_search_form(driver)

            fill_search_form_for_term(driver, tname)

            term_rows = 0
            page = 1

            while True:
                print(f"  📄 Page {page}...")
                rows = scrape_sections_from_current_page(driver, tname)
                print(f"    → {len(rows)} rows found.")
                term_rows += len(rows)
                all_rows.extend(rows)

                if not click_next_if_possible(driver):
                    break
                page += 1

            print(f"  ✅ Finished {tname}: {term_rows} rows")
            go_back_to_search_form(driver)

        print(f"\n🎯 TOTAL rows: {len(all_rows)}")

        fieldnames = [
            "term",
            "course_id",
            "crn",
            "section",
            "day_of_week",
            "start_min",
            "end_min",
            "room",
            "instruction_mode",
            "professor",
            "status",
        ]

        # Save single CSV
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

        print("\n📁 Saved CSV:", os.path.abspath(OUTPUT_CSV))

        # Upload to backend
        upload_csv(OUTPUT_CSV)

    finally:
        print("\nClosing browser in 10 seconds…")
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    main()
