import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urlsplit
import re
from collections import deque
from concurrent.futures import ThreadPoolExecutor

complicatedRegex = re.compile(r"([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)?)") // best ever regex for email scraping

new_urls = deque()

def add_to_queue():
    for line in open('emailFinder.txt'):
        new_urls.append(line.strip())

def request_page(url):
    try:
        r = requests.get(url)
        return r.text
    except:
        pass

def check_email(html):
    emails = re.findall(complicatedRegex, str(html))
    mails = []
    for mail in emails:
        a,b,c = mail
        #print(a)
        mails.append(a)
    #print(mails)
    return mails

def grab_links(html,url):
    list_of_links = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        parts = urlsplit(url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = url[:url.rfind('/') + 1] if '/' in parts.path else url
        for anchor in soup.find_all("a"):
            anchor = anchor['href']
            if anchor.startswith('/'):
                scheme = urlparse(url).scheme
                netloc = urlparse(url).netloc
                anchor = '{}://{}{}'.format(scheme, netloc, anchor)
                list_of_links.append(anchor)
            if urlparse(anchor).netloc != urlparse(url).netloc:
                pass
            else:
                list_of_links.append(anchor)
    except:
        pass
    return list_of_links

def write_to_csv(url,email_list):
    string = ','.join(email_list)
    final_string = '{},{}\n'.format(url,string)
    if len(email_list) > 0:
        with open('Results.csv','a',encoding='utf-8') as file:
            file.write(final_string)

def main():
    add_to_queue()
    while len(new_urls) > 0:
        url = new_urls.pop()
        list_of_urls = []
        mail = []
        done_urls = []
        html = request_page(url)
        list_of_links = grab_links(html,url)
        emails = check_email(html)
        for link in list_of_links:
            list_of_urls.append(link)
        for email in emails:
            mail.append(email)
        write_to_csv(url,mail)
        for link in list_of_urls:
            if link not in done_urls:
                html = request_page(link)
                mails = check_email(html)
                write_to_csv(link,mails)
                done_urls.append(link)

main()
