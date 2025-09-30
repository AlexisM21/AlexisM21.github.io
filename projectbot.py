import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# opens the website 
opts = Options()
opts.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=opts)
driver.get("https://cmsweb.fullerton.edu/psc/CFULPRD/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?&public")

dropdown= driver.find_element(By. ID, "CLASS_SRCH_WRK2_STRM$35$")
dd= Select(dropdown)

term_select= dd.select_by_index(1)

for i in term_select:
    term_select= dd.select_by_index(i)
        


# #def elem_finder(driver, loc_type, loc_value):
# #    '''determines the location type to be passed into select_dropdown'''

# def locator_map(driver, loc_type, loc_value):
#     '''maps the locator type to fit into Seleniums .find_element'''
#     locators = {
#         'id': By.ID,
#         'name': By.NAME,
#         'xpath': By.XPATH,
#         'css': By.CSS_SELECTOR,
#         'class_name': By.CLASS_NAME,
#         'tag_name': By.TAG_NAME
#     }

#     loc_type= loc_type.lower()
#     if loc_type not in locators:
#         raise ValueError(f'Unsupported locator type: {loc_type}')
    
#     by= locators[loc_type]
#     return driver.find_element(by, loc_value)

# def select_dropdown(driver, loc_type, loc_val, method):
#     '''wrapper helper function to replace seleniums Select FOR DROPDOWNS ONLY'''
#     find= locator_map(driver, loc_type, loc_val)
#     opt_select= Select(find)

#     # determines and assigns by value
#     if loc_type == 'text':
#         opt_select.select_by_visible_text(method)
#     elif loc_type == 'id':
#         opt_select.select_by_value(method)
#     elif loc_type == 'index':
#         opt_select.select_by_index(method)

    

# # finds the term dropdown menu
# #term_dropdown = driver.find_element(By.ID, "CLASS_SRCH_WRK2_STRM$35$")


# term_dropdown= select_dropdown(driver, 'id', "CLASS_SRCH_WRK2_STRM$35$", '2257')

# Passing to Select (tells selenium to interact with a dropdown menu)
#term_select= Select(term_dropdown)
#term_select.select_by_value("2257") #fall sem

# sub_select= 
