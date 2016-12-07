import requests
import re
from urllib.parse import urlparse
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

site_list = [line.rstrip('\n') for line in open(r'sites.txt')]

#site_list = ['http://www.fx-today.com']

domain_list = []

def parse_sites():
    site = site_list.pop()
    parse = urlparse(site)
    return '{}://{}'.format(parse.scheme,parse.netloc)

def generate_regex(domain):
    domain = domain.replace('.','\.')
    domain = domain.replace("\\",'\\')
    regex = re.compile('{}{}'.format(domain,'.*'))
    return regex

def grab_page(page):
    try:
        r = requests.get(page)
        return r.text
    except:
        return ''

def grab_links(html,url,regex):
    list_of_links = []
    soup = BeautifulSoup(html,'lxml')
    parts = urlsplit(url)
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    path = url[:url.rfind('/') + 1] if '/' in parts.path else url
    for anchor in soup.find_all("a"):
        anchor = anchor['href']
        if anchor.startswith('/'):
            scheme = urlparse(url).scheme
            netloc = urlparse(url).netloc
            anchor = '{}://{}{}'.format(scheme,netloc,anchor)
            list_of_links.append(anchor)
        if urlparse(anchor).netloc != urlparse(url).netloc:
            pass
        else:
            list_of_links.append(anchor)
    #print(list_of_links)
    return list_of_links

def check_email(html):
    emails = re.findall(r"([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", str(html))
    mails = []
    for mail in emails:
        a,b,c = mail
        #print(a)
        mails.append(a)
    #print(mails)
    return mails

def write_to_csv(url,email_list):
    string = ','.join(email_list)
    final_string = '{},{}\n'.format(url,string)
    with open('Results.csv','a',encoding='utf-8') as file:
        file.write(final_string)


def site_parser():
    for site in site_list:
        domain = parse_sites()
        domain_list.append(domain)

def email_grabber():
    for domain in domain_list:
        re1 = '{}{}'.format(domain,'.*')
        regex = re.compile(re1)
        html = grab_page(domain)
        list_of_links = grab_links(html,domain,regex)
        list_of_emails = check_email(html)
        #print(list_of_emails)
        empty_email_list = []
        for email in list_of_emails:
            if email not in empty_email_list:
                empty_email_list.append(email)
        for link in list_of_links:
            html = grab_page(link)
            emails_found = check_email(html)
            for mail in emails_found:
                if mail not in empty_email_list:
                    empty_email_list.append(mail)
        write_to_csv(domain,empty_email_list)

def main():
    site_parser()
    email_grabber()

main()




