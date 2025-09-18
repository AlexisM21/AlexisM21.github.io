from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=opts)
driver.get("https://cmsweb.fullerton.edu/psc/CFULPRD/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?&public")
