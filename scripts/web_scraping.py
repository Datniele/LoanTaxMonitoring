from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from os import listdir
import pandas as pd
import re


class GetTextForScraping(object):
    def __init__(self, **kwargs):
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(kwargs.get("str_url"))
        page_source = driver.page_source
        self.soup = BeautifulSoup(page_source, features="html.parser")
        driver.quit()


class TaxLoanScraping(GetTextForScraping):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def find_section(self):

        lst_h3 = self.soup.main.section.find_all("h3")
        int_target = -10
        str_target = 'Miglior mutuo per acquisto prima casa'
        for i, h3_tag in enumerate(lst_h3):
            lst_a = h3_tag.find_all("a")
            lst_title = [a_tag["title"] for a_tag in lst_a]
            if str_target in lst_title:
                int_target = i
                break

        h3_target = lst_h3[int_target]
        div_target = h3_target.find_next("div", class_="table-center table-overflow table-tablet")
        return div_target

    @staticmethod
    def parsing_result(obj_target):

        lst_columns = [strong.text for strong in obj_target.find_all("strong")]

        lst_banks = [re.sub(r"\s+|\\n", "", a_tag.text) for a_tag in obj_target.find_all("a")]

        lst_td_target = [td_obj for td_obj in obj_target.find_all("td") if not td_obj.find("a")]

        lst_first_bank = [re.sub(r"\s+|\\n", "", td_obj.text) for td_obj in lst_td_target[:3]]
        lst_second_bank = [re.sub(r"\s+|\\n", "", td_obj.text) for td_obj in lst_td_target[3:]]

        str_type_first_bank = re.search(r'\((.*?)\)', lst_first_bank[0]).group(1)
        str_type_second_bank = re.search(r'\((.*?)\)', lst_second_bank[0]).group(1)

        lst_first_bank = [re.search(r"\d+(.|,)\d+", val).group() for val in lst_first_bank] + [str_type_first_bank]
        lst_second_bank = [re.search(r"\d+(.|,)\d+", val).group() for val in lst_second_bank] + [str_type_second_bank]

        lst_first_bank = [lst_banks[0]] + [float(re.sub(",", ".", val)) if val != str_type_first_bank else
                                           val for val in lst_first_bank]
        lst_second_bank = [lst_banks[1]] + [float(re.sub(",", ".", val)) if val != str_type_second_bank else
                                            val for val in lst_second_bank]

        lst_dtf = [lst_first_bank, lst_second_bank]

        dtf_out = pd.DataFrame(lst_dtf, columns=lst_columns + ["TipoTasso"])

        str_date = datetime.today().strftime('%Y-%m-%d')

        dtf_out["Date"] = pd.to_datetime(str_date)

        return dtf_out

    def get_scraping_result(self, bln_write=True):
        obj_target = self.find_section()
        dtf_out = self.parsing_result(obj_target)

        lst_file = listdir("data")
        if lst_file:
            dtf_old = pd.read_pickle("data/dtf_tax_history.pickle")
            if dtf_old["Date"].max() < dtf_out["Date"].max():
                dtf_out = pd.concat([dtf_old, dtf_out])
            else:
                bln_write = False

        if bln_write:
            dtf_out.to_pickle("data/dtf_tax_history.pickle")

        return dtf_out


# dentro main
# dentro section
# h3 class
# trovo il titolo relativo a mutuo prima casa
# next tabella
# parso


# lst_h3 = tls.soup.main.section.find_all("h3")
# int_target = -10
# str_target = 'Miglior mutuo per acquisto prima casa'
# for i, h3_tag in enumerate(lst_h3):
#     lst_a = h3_tag.find_all("a")
#     lst_title = [a_tag["title"] for a_tag in lst_a]
#     if str_target in lst_title:
#         int_target = i
#         break
#
# h3_target = lst_h3[int_target]
# div_target = h3_target.find_next("div", class_="table-center table-overflow table-tablet")
#
# # parsing table
#
# lst_columns = [strong.text for strong in div_target.find_all("strong")]
#
# lst_banks = [re.sub(r"\s+|\\n", "", a_tag.text) for a_tag in div_target.find_all("a")]
#
# lst_td_target = [td_obj for td_obj in div_target.find_all("td") if not td_obj.find("a")]
#
# lst_first_bank = [re.sub(r"\s+|\\n", "", td_obj.text) for td_obj in lst_td_target[:3]]
# lst_second_bank = [re.sub(r"\s+|\\n", "", td_obj.text) for td_obj in lst_td_target[3:]]
#
# str_type_first_bank = re.search(r'\((.*?)\)', lst_first_bank[0]).group(1)
# str_type_second_bank = re.search(r'\((.*?)\)', lst_second_bank[0]).group(1)
#
# lst_first_bank = [re.search(r"\d+(.|,)\d+", val).group() for val in lst_first_bank] + [str_type_first_bank]
# lst_second_bank = [re.search(r"\d+(.|,)\d+", val).group() for val in lst_second_bank] + [str_type_second_bank]
#
# lst_first_bank = [lst_banks[0]] + [float(re.sub(",", ".", val)) if val != str_type_first_bank else
#                                    val for val in lst_first_bank]
# lst_second_bank = [lst_banks[1]] + [float(re.sub(",", ".", val)) if val != str_type_second_bank else
#                                     val for val in lst_second_bank]
#
# lst_dtf = [lst_first_bank, lst_second_bank]
#
#
# dtf_out = pd.DataFrame(lst_dtf, columns=lst_columns + ["TipoTasso"])
#
# str_date = datetime.today().strftime('%Y-%m-%d')
#
# dtf_out["Date"] = pd.to_datetime(str_date)
#
#
# lst_file = listdir("data")
# if lst_file:
#     dtf_old = pd.read_pickle("data/dtf_tax_history.pickle")
#     if dtf_old["Date"].max() < dtf_out["Date"].max():
#         dtf_out = pd.concat([dtf_old, dtf_out])
#
# dtf_out.to_pickle("data/dtf_tax_history.pickle")
