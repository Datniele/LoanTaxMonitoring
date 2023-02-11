import json
from scripts.mail_sender import MailSender
from scripts.web_scraping import TaxLoanScraping
from scripts.tax_analysis import tax_var_analysis
from datetime import datetime
import pandas as pd
from os import listdir

today = datetime.today()
bln_mail_go = True
dct_last_mail = dict()

dct_conf = {"str_url": "https://mutuionline.24oreborsaonline.ilsole24ore.com"
                       "/mutuo-migliore/miglior-mutuo.asp?refresh_ce=1"}

tls = TaxLoanScraping(**dct_conf)
# bln_write True per default
dtf_tax_history = tls.get_scraping_result()

print("Scraping done!")

# analisi tassi

dtf_tax = dtf_tax_history.query("TipoTasso == 'fisso'").copy()
dct_summary = tax_var_analysis(dtf_tax)

print("Loan Tax Analysis done!")

if dct_summary:
    flt_tax = round(dct_summary.get("tax_delta"), 3)*100
    dtf_summary = dct_summary.get("summary")
    flt_tm = dtf_summary.query("AM == AM.max()")["TAX_MEAN"].values[0]
    flt_lm = dtf_summary.query("AM == AM.min()")["TAX_MEAN"].values[0]
    str_corpus = f"""
    C'è stata una variazione nel tasso d'interesse medio degli ultimi due mesi del {flt_tax}%.
    Il tasso medio di questo mese è {flt_tm}%.
    Il tasso medio del mese scorso è {flt_lm}%
    
    Daniele
             """
    if "last_mail.json" in listdir("data"):
        with open("data/last_mail.json", "r") as f:
            dct_last_mail = json.load(f)
        lst_mail_date = datetime.strptime(dct_last_mail.get("last"), "%d-%m-%Y")
        delta = today - lst_mail_date
        if delta.days < 10:
            bln_mail_go = False


else:
    str_corpus = "Il tasso d'interesse medio mensile non ha subito una variazione significativa.\n\nDaniele"


if bln_mail_go:
    dct_last_mail["last"] = today.strftime("%d-%m-%Y")
    with open('data/last_mail.json', 'w', encoding='utf-8') as f:
        json.dump(dct_last_mail, f, ensure_ascii=False, indent=4)

    # MAIL SENDER
    dct_login = pd.read_pickle("config/mail_login.pickle")

    ms = MailSender(dct_login)

    str_to = "dani.testav@gmail.com"
    str_subj = "Report tassi d'interesse"

    ms.mail_configure(str_email_receiver=str_to, str_subject=str_subj, str_corpus=str_corpus)

    ms.mail_sender()

    print("Mail sent!")

