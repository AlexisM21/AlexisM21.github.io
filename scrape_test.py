# DELETE FILE

import os, tempfile, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# ---- Candidate endpoints (we'll try each until the search form appears) ----
CANDIDATE_URLS = [
    # Your original
    "https://cmsweb.fullerton.edu/psc/CFULPRD/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?&public&",
    # Common PeopleSoft content path
    "https://cmsweb.fullerton.edu/psp/CFULPRD/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?&public&",
    # Campus Solutions node sometimes exposes public pages here
    "https://cmsweb.fullerton.edu/psc/CFULPRD/CS/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?&public&",
    "https://cmsweb.fullerton.edu/psp/CFULPRD/CS/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?&public&",
    # Direct entry page (some schools require this Page param)
    "https://cmsweb.fullerton.edu/psc/CFULPRD/CS/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U&public=Y",
    "https://cmsweb.fullerton.edu/psp/CFULPRD/CS/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U&public=Y",
]

# ---------- Chrome setup ----------
opts = Options()
# Persist cookies in a temp profile (so they aren't wiped each run)
user_data_dir = os.path.join(tempfile.gettempdir(), "chloe_csuf_profile")
os.makedirs(user_data_dir, exist_ok=True)
opts.add_argument(f"--user-data-dir={user_data_dir}")
opts.add_argument("--profile-directory=Default")

# Allow cookies (incl. 3rd party)
opts.add_argument("--disable-features=BlockThirdPartyCookies")
opts.add_experimental_option("prefs", {
    "profile.default_content_setting_values.cookies": 1,
    "profile.block_third_party_cookies": False,
})

# Make automation a bit less obvious (some portals are picky)
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)
opts.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=opts)

# ---------- Helpers ----------
def enter_content_context(driver, timeout=10, poll=0.25):
    """
    Make the class-search form interactable.
    Returns (in_iframe: bool, where: str).
    """
    end = time.time() + timeout
    driver.switch_to.default_content()

    def has_form_here():
        try:
            driver.find_element(By.XPATH, "//select[contains(@id,'STRM') or contains(@id,'SUBJECT')]")
            return True
        except Exception:
            return False

    if has_form_here():
        return (False, "top-document")

    last_count = -1
    while time.time() < end:
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        if len(frames) != last_count:
            print(f"[debug] found {len(frames)} iframe(s)")
            last_count = len(frames)

        for attr, val in [("id", "ptifrmtgtframe"), ("name", "ptifrmtgtframe"),
                          ("id", "TargetContent"), ("name", "TargetContent")]:
            try:
                frame = driver.find_element(By.XPATH, f"//iframe[@{attr}='{val}']")
                driver.switch_to.frame(frame)
                if has_form_here(): return (True, val)
                try:
                    inner = driver.find_element(By.XPATH, "//iframe[@id='TargetContent' or @name='TargetContent']")
                    driver.switch_to.frame(inner)
                    if has_form_here(): return (True, f"{val} -> TargetContent")
                except Exception:
                    pass
                driver.switch_to.default_content()
            except Exception:
                pass

        if frames:
            try:
                driver.switch_to.frame(frames[0])
                if has_form_here(): return (True, "first-iframe")
                try:
                    inner = driver.find_element(By.XPATH, "//iframe[@id='TargetContent' or @name='TargetContent']")
                    driver.switch_to.frame(inner)
                    if has_form_here(): return (True, "first-iframe -> TargetContent")
                except Exception:
                    pass
            except Exception:
                pass
            finally:
                driver.switch_to.default_content()

        time.sleep(poll)

    print("[debug] no iframe with form yet; staying in top document")
    return (False, "top-document")

def click_one_of(xpaths, pause=1.0):
    for xp in xpaths:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            els[0].click()
            time.sleep(pause)
            return True
    return False

def ensure_on_form(max_steps=3):
    """
    From a landing/portal/cookie page, navigate into the Class Search form.
    """
    # Cookie gate? Try refresh once.
    cookie_gate = driver.find_elements(
        By.XPATH,
        "//*[contains(translate(.,'COOKIES','cookies'),'cookies') and contains(translate(.,'ENABLE','enable'),'enable')]"
    )
    if cookie_gate:
        print("[debug] cookie gate detected; refreshing")
        driver.refresh()
        time.sleep(1.5)

    for _ in range(max_steps):
        enter_content_context(driver)
        # Is form visible now?
        try:
            driver.find_element(By.XPATH, "//select[contains(@id,'STRM') or contains(@id,'SUBJECT')]")
            return True
        except Exception:
            pass

        # Try typical links/tiles that lead to class search
        clicked = click_one_of([
            "//a[.//span[normalize-space()='Class Search']]",
            "//a[contains(.,'Class Search') or contains(.,'Search for Classes')]",
            "//input[@type='button' or @type='submit'][@value='Search']",
            "//*[@id='PTNUI_LAND_REC_GROUPLET$0' or @id='PTNUI_LAND_REC_GROUPLET$1']",
            "//a[normalize-space()='Sign in to PeopleSoft']",  # if this shows on the cookie page
        ], pause=1.2)

        if not clicked:
            break

    return False

def get_select(locator_xpath):
    el = driver.find_element(By.XPATH, locator_xpath)
    return Select(el)

def click_if_present(by, value):
    els = driver.find_elements(by, value)
    if els:
        els[0].click()
        return True
    return False

def try_open_until_form(urls):
    """Open each candidate URL until we see the form selects."""
    for url in urls:
        print(f"\n[debug] trying URL: {url}")
        driver.get(url)
        time.sleep(2.0)

        # If we hit a cookie/interstitial, try to navigate to the form
        if ensure_on_form():
            print(f"[debug] reached form via: {url}")
            return True

        # Final check without helper
        enter_content_context(driver)
        try:
            driver.find_element(By.XPATH, "//select[contains(@id,'STRM') or contains(@id,'SUBJECT')]")
            print(f"[debug] form detected directly at: {url}")
            return True
        except Exception:
            pass

    return False

# ---------- Main ----------
try:
    if not try_open_until_form(CANDIDATE_URLS):
        raise RuntimeError("Could not reach the public Class Search form (stuck at cookie/login). Try running once manually in this Chrome window, then rerun.")

    in_iframe, where = enter_content_context(driver)
    print(f"[debug] working context: {where} (in_iframe={in_iframe})")

    # Locate selects
    term_xpath = "//select[contains(@id,'STRM')]"
    subj_xpath = "//select[contains(@id,'SUBJECT')]"
    term_select = get_select(term_xpath)
    subject_select = get_select(subj_xpath)

    # Small test set
    all_terms = [o.text.strip() for o in term_select.options if o.text and o.text.strip()]
    all_subjects = [o.text.strip() for o in subject_select.options if o.text and o.text.strip()]
    test_terms = all_terms[:1]
    test_subjects = all_subjects[:3]
    print("Testing terms:", test_terms)
    print("Testing subjects:", test_subjects)

    # Loop
    for term_label in test_terms:
        term_select = get_select(term_xpath)
        term_select.select_by_visible_text(term_label)
        time.sleep(0.5)

        for subj_label in test_subjects:
            subject_select = get_select(subj_xpath)
            subject_select.select_by_visible_text(subj_label)
            time.sleep(0.3)

            # Search
            clicked = False
            for cand in [
                (By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH"),
                (By.XPATH, "//input[contains(@id,'SSR_PB_CLASS_SRCH') or @value='Search']"),
            ]:
                if click_if_present(*cand):
                    clicked = True
                    break
            if not clicked:
                raise RuntimeError("Search button not found.")

            time.sleep(2.0)
            click_if_present(By.ID, "ICOK")
            click_if_present(By.XPATH, "//input[@type='button' and @value='OK']")
            time.sleep(0.6)

            # Sample scrape
            titles    = driver.find_elements(By.XPATH, "//span[contains(@id,'MTG_CLASSNAME')]")
            classnbrs = driver.find_elements(By.XPATH, "//span[contains(@id,'CLASS_NBR')]")
            daytimes  = driver.find_elements(By.XPATH, "//span[contains(@id,'MTG_DAYTIME')]")
            instrs    = driver.find_elements(By.XPATH, "//span[contains(@id,'MTG_INSTR')]")

            print(f"\n=== {term_label} / {subj_label} ===")
            n = max(len(titles), len(classnbrs), len(daytimes), len(instrs))
            if n == 0:
                blocks = driver.find_elements(By.XPATH, "//*[self::table or self::div][contains(., 'Class')]")
                print(f"Found {len(blocks)} possible result blocks (adjust locators after inspecting).")
            else:
                for i in range(min(n, 5)):
                    t = titles[i].text.strip() if i < len(titles) else ""
                    c = classnbrs[i].text.strip() if i < len(classnbrs) else ""
                    d = daytimes[i].text.strip() if i < len(daytimes) else ""
                    ins = instrs[i].text.strip() if i < len(instrs) else ""
                    print(f"- {c} | {t} | {d} | {ins}")

            # Return to search
            went_back = False
            for cand in [
                (By.ID, "CLASS_SRCH_WRK2_SSR_PB_BACK"),
                (By.XPATH, "//input[contains(@id,'SSR_PB_BACK') or @value='Return to Search']"),
            ]:
                if click_if_present(*cand):
                    went_back = True
                    break
            if not went_back:
                driver.back()

            time.sleep(1.5)
            enter_content_context(driver)
            # re-acquire selects
            term_select = get_select(term_xpath)
            subject_select = get_select(subj_xpath)

    print("\nDone. If you still get the cookie page, leave this Chrome window open, click “Sign in to PeopleSoft” once, accept any prompts, close the tab, and rerun the script so the cookie persists in the saved profile.")

finally:
    # Keep open for debugging; uncomment to auto-close:
    # driver.quit()
    pass
