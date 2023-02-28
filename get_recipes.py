from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import time

URL = f"https://www.simplyrecipes.com/recipes-5090746"
FILE_NAME = 'recipe_links_simplyrecipes.txt'
EMPTY_LINKS = 'recipe_empty.txt'
PATTERN = 'simplyrecipes.com'


def connect(url=URL):
    """
    create chrome driver
    :return: chrome driver:obj
    """
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
    try:
        driver.get(url)
        time.sleep(5)
    except TimeoutException:
        print('new connection try')
        driver.get(url)
        time.sleep(5)

    return driver


def get_links_from_page(my_webpage):
    """
    To collect links for each recipe from one page
    :param my_webpage: link to page for scrapping: selenium obj
    :return: links from one page: list[str]
    """
    recipe_links = []
    # we know that on this website we have 26 links per page
    for i in range(5):
        try:
            if i < 1:
                recipe = my_webpage.find_element(By.XPATH,
                f'//*[@id="mntl-card-list-items_2-{i}"]')
            else:
                recipe = my_webpage.find_element(By.XPATH,
                f'//*[@id="mntl-card-list-items_2-0-{i}"]')
            print( recipe)
        except:
            continue
        recipe_links.append(recipe.get_attribute("href"))
    return recipe_links



def get_links_from_site(recipe_driver):
    """
    To list pages on website and collect links into list
    :param recipe_driver: obj  chrome driver
    :param num_pages: int number of pages to scrap / default 132
    :return: list of links
    """
    all_pages_links = []
    for i in range(1):

        # get links from one page
        page = get_links_from_page(recipe_driver)
        all_pages_links.append(page)

    return all_pages_links


def extract_links_to_file(file_name):
    """
    To write down links into .txt file
    :param file_name: output filename / FILE_NAME in the same dir
    :return: void
    """
    # create a driver
    recipe_driver = connect()

    # collect links
    recipe_links = get_links_from_one_page(recipe_driver)

    # write down links to the txt file
    output_recipe_links = open(file_name, 'w')
    empty_links = open(EMPTY_LINKS, 'w')
    for link_list in recipe_links:
        for url in link_list:
            if url.__contains__(PATTERN):
                output_recipe_links.write(url + '\n')
            else:
                empty_links.write(url + '\n')
    output_recipe_links.close()
    empty_links.close()

    print(f'links are in {file_name} file')


def get_recipe(link):
    """
    To collect recipe ingredients and instructions into dictionary
    with keys "Recipe" and "INSTRUCTIONS", text  - values
    :param link: str
    :return: json_file: dict()
    """
    json_file = {}  # not real json just regular dictionary
    ingredients_list = []
    instructions_list = []

    # create a driver for concrete page
    recipe_driver = connect(link)

    # get ingredients
    try:
        result_ingr = recipe_driver.find_element(By.XPATH,'//*[@class="structured-ingredients__list-item"]')

    # check for recaptcha/invisible recaptcha
    except NoAlertPresentException:
        WebDriverWait(recipe_driver, 5).until(EC.alert_is_present(), 'Timed out waiting for alerts to appear')
        alert = recipe_driver.switch_to.alert
        alert.accept()
        print("alert accepted")
        result_ingr = recipe_driver.find_element(By.XPATH,'//*[@class="structured-ingredients__list-item"]')

    # get 'ul' elements with ingredient text
    # options_ingr = result_ingr.find_element(By.TAG_NAME,"ul")

    #  we will get text only if 'ul' element is not empty [], ''. if it is --> check a div nearby
    # if not options_ingr:
    #     result_ingr = recipe_driver.find_element(By.XPATH,'// *[ @ id = "sr-recipe-callout"] / div[3]')
    #     options_ingr = result_ingr.find_element(By.TAG_NAME,"ul")
    # for paragr in options_ingr:
    #     ingredients_list.append(paragr.text)

    # get instructions paragraphs
    # result_instr = recipe_driver.find_element(By.XPATH,
    #     '//*[@id="sr-recipe-method"]/div')
    # options_instr = result_instr.find_element(By.TAG_NAME,"p")
    # for paragraph in options_instr:
    #     if paragraph.text != '':
    #         instructions_list.append(paragraph.text.strip())

        # if paragraph.text is empty str we moving on to the next paragraph
        # else:
        #     continue
    recipe_driver.close()

    # create a dictionary with recipe and instructions text
    json_file["Recipe"] = '\n\n'.join(ingredients_list)
    json_file['INSTRUCTIONS'] = '\n\n'.join(instructions_list)

    return json_file


def print_json(url_to_get_recipe, json_file, counter=1):
    """
    To print to the console json beautiful format
    :param url_to_get_recipe:str
    :param json_file:dict
    :return void
    """

    print(str(counter) + " Url: {} \n{{\n \t\t{} :\n\t\t\t\t[".format(url_to_get_recipe, list(json_file.keys())[0]))
    for i in json_file['Recipe'].split('\n'):
        print('\t\t\t\t\t\t {}'.format(i))
    print('\t\t\t\t]')
    print('\n\t\t' + str(list(json_file.keys())[1] + ':'))
    print('"' + json_file['INSTRUCTIONS'] + '"')
    print('}\n')


if __name__ == '__main__':
    pass