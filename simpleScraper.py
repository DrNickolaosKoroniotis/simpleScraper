#!/usr/bin/env python
import os.path
import time
import requests
import argparse
import re
from bs4 import BeautifulSoup
sepLength=20
sepCharacter="~"
errCharacter="x"
successCharacter="+"
visit=[]
visited=[]
crawling=[]
visited_robots=[]
def flattenList(args):
    res=[]
    for i in args:
        if type(i)==list:
            buf=flattenList(i)
            res.extend(buf)
        else:
            res.append(i)
    return res

def print_msg_arguments(*args):
    global sepLength,sepCharacter
    msg=sepCharacter+" Received arguments: "+" ".join([str(elmnt) for elmnt in flattenList(args)])
    print(sepCharacter*(len(msg)-1))
    print(msg)
    print(sepCharacter*(len(msg)-1))

def print_error_message(*args):
    global sepLength, errCharacter
    CRED = '\033[91m'
    CEND = '\033[0m'
    extra_space = False
    msg = errCharacter +  " ".join([str(elmnt) for elmnt in flattenList(args)])
    print(CRED+errCharacter * (len(msg)))
    if extra_space:
        print(errCharacter)
    print(msg)
    if extra_space:
        print(errCharacter)
    print(errCharacter * (len(msg))+CEND)

def print_success_message(*args):
    global sepLength, successCharacter
    CGREEN = '\033[92m'
    CEND = '\033[0m'
    extra_space = False
    msg = successCharacter +  " ".join([str(elmnt) for elmnt in flattenList(args)])
    print(CGREEN+successCharacter * (len(msg)))
    if extra_space:
        print(successCharacter)
    print(msg)
    if extra_space:
        print(successCharacter)
    print(successCharacter * (len(msg))+CEND)

def print_generic_message(msg,*args):
    global sepLength, sepCharacter
    extra_space = False
    msg = sepCharacter + f" {msg}" + " ".join([str(elmnt) for elmnt in flattenList(args)])
    print(sepCharacter * (len(msg)))
    if extra_space:
        print(sepCharacter)
    print(msg)
    if extra_space:
        print(sepCharacter)
    print(sepCharacter * (len(msg)))

search=[]
avoid=[]
def get_robot_general(text):
    found=False
    for line in text.split("\n"):
        if line.startswith("#"):
            continue
        elif line == "User-agent: *":
            found=True
            continue
        if found:
            if line.startswith("Disallow:"):
                avoid.append(line.replace("Disallow: ",""))
            elif line.startswith("Allow:"):
                search.append(line.replace("Allow: ",""))
            if line.startswith("User-agent") and line != "User-agent: *":
                break

def check_robot(url):
    url_base=get_base_URL(url)
    visited_robots.append(url_base)
    url_robot=url_base+"/robots.txt"
    print_generic_message("Searching for 'robots.txt' on ",url)
    resp=requests.get(url_robot)
    if resp.status_code>=200 and resp.status_code<300:
        print_generic_message("File 'robots.txt' found at ",url)
        body=resp.text
        get_robot_general(body)
        print_generic_message(msg=f"Found {len(search)} allowed and {len(avoid)} disallowed paths!")


def get_base_URL(url):
    return re.findall(r"http[s]?://[^/]+", url)[0]
def get_article_name(url):
    return re.sub(get_base_URL(url),"", url)
def fetch(url):

    url_base=get_base_URL(url)
    url_path=url.replace(url_base,"")

    print_generic_message(f"Checking if path of {url} is permitted!")
    if url_path in avoid:
        print_error_message(f"Provided URL path '{url_path}' not permitted by robot.txt!")
        return False
    else:
        resp=requests.get(url)
        if resp.status_code>=200 and resp.status_code<300:
            respB=BeautifulSoup(resp.text,"html.parser")
            return respB

def check_local_storage_dirs(url):
    try:
        url_base=re.findall(r"http[s]?://[^/]+",url)[0]
        p1=re.sub(r"^http[s]?://","",url_base)
        path="./"+p1.replace(".","_")
        if not os.path.isdir(path):
            os.mkdir(path)

        return path
    except Exception as e:
        print_error_message(e)
        return None

def alter_title_articles(title):
    title=title.rstrip().lstrip()
    return re.sub(r"[ -/]+","_",title)
def check_article_path(title,path):
    try:
        pth=path+"/"+alter_title_articles(title)
        if not os.path.isdir(pth):
            os.mkdir(pth)

        return pth
    except:
        return None

def check_html_dir(path):
    if not os.path.isdir(path+"/html"):
        os.mkdir(path+"/html")

    return path+"/html"
def save_resp(resp, path, title):
    path=check_html_dir(path)
    with open(path + "/" + alter_title_articles(title) + "_article.html", "w") as fwa:
        fwa.write(resp)
        fwa.flush()

def check_subarticle_path(path):
    if not os.path.isdir(path+"/subarticles"):
        os.mkdir(path+"/subarticles")
    return path+"/subarticles"
def strip(resp, path, title,strategy="1"):

    text=""
    path=check_article_path(title,path)
    if strategy in ["1","both"]:
        print_generic_message("Leveraging Strategy 1.")

        content_div=resp.find_all("p")
        for cont in content_div:
            if len(cont.text)>0:
                buf=cont.text
                buf=buf.lstrip().rstrip()
                buf=re.sub(r"\[[0-9]+\]","",buf)#Remove references to keep pure text.
                buf.replace("''","'")
                text+=buf+"\n"
        with open(path + "/"+ alter_title_articles(title) + "_extracted_text", "w") as fwa:
            fwa.write(text)
            fwa.flush()
    if strategy in ["2","both"]:
        print_generic_message("Leveraging Strategy 2.")

        newPath=check_subarticle_path(path)
        #Strategy 2 here.

        results = (resp.find_all(re.compile(r"(h\d+)|(^p$)")))
        buffer = []
        for elmnt in results:
            if len(buffer) == 0:#If stack is empty, populate.
                buffer.append(elmnt)
            else:
                if bool(re.search("h\d+", elmnt.name)):#If next element is h[0-0]
                    if len(buffer) > 1:#And we have more than one element in the stack.
                        if not bool(re.search("^p$", buffer[1].name)):
                            buffer.pop(0)
                            continue
                        with open(newPath+"/"+buffer[0].text.replace("/","_")+".txt","w") as fw:
                            buffer.pop(0)
                            while len(buffer) > 0:
                                buf = buffer[0].text
                                buf = buf.lstrip().rstrip()
                                buf = re.sub(r"\[[0-9]+\]", "", buf)
                                buf.replace("''", "'")
                                fw.write(buf)
                                buffer.pop(0)
                    else:
                        buffer.pop()
                    buffer.append(elmnt)
                elif bool(re.search("^p$", elmnt.name)):
                    buffer.append(elmnt)
def crawl_offline(resp,URL,breadth=5,debug=False):
    print_generic_message(f"Crawling from {URL}. Breadth set to {breadth}")
    url_base = get_base_URL(URL)
    url_path = url.replace(url_base, "")
    if URL in visited or URL in avoid:
        print_generic_message(f"Skipping {URL}!"+("Already visited" if URL in visited else "URL specified as 'avoid' by robot.txt"))
    elif url_path in visited or url_path in avoid:
        print_generic_message(f"Skipping {URL}!"+("Already visited" if URL in visited else "URL specified as 'avoid' by robot.txt"))
    else:
        found_article_div=resp.find("div",class_="mw-body-content",id="mw-content-text")
        found_links=found_article_div.find_all("a")
        counter=0
        ret_links=[]
        for a in found_links:
            if a["href"].startswith("/"):
                if a["href"] in avoid or a["href"] in visited or url_base+a["href"] in avoid or url_base+a["href"] in visited:
                    continue
                else:
                    if counter<breadth:
                        if not url_base+a["href"] in ret_links and not any(i in url_base+a["href"] for i in [".jpg",".png","File:","(disambiguation)","Wikipedia:","View source","Help:","Special:","EditPage","Talk:","Portal:"]):
                            ret_links.append(url_base+a["href"])
                            print(ret_links) if debug else None
                            counter+=1
                    else:
                        break

        return ret_links
    return None


if __name__=="__main__":
    negative_choice=["0","False","false","f","F","n","N","no","NO","No"]
    positive_choice=["1","True","true","t","T","y","Y","yes","Yes","YES"]
    parser=argparse.ArgumentParser(prog="simpleScraper",description="This is a simple web scraper that takes into account any 'robots.txt' prior to downloading.",epilog="A project by Koro.")
    parser.add_argument("--url","-u",dest="url",required=True,help="Set the URL that the scraper will target.")
    parser.add_argument("--delay",type=float,dest="delay",default=0.5, help="Set the delay (in seconds) before each request is sent.")
    parser.add_argument("--strategy",choices=["1","2","both"],dest="strategy",default="1", help="Set the strategy for extracting text from the websites. Strategy 1 finds every paragraph and accumulates their text, extractng it in a single text document. Strategy 2 creates a new subfolder and one text file per section of text (separating it acording to titles and sections found).")
    parser.add_argument("--crawl",choices=negative_choice+positive_choice,dest="crawl",default="False", help="Enable or disable the crawling option. If enabled, scraper will crawl through any URL of the same domain as the original URL, up to a depth of 5. To enable, provide any of the following {}. To disable, provide any of the following {}.".format(str(positive_choice),str(negative_choice)))
    parser.add_argument("--breadth",choices=range(0,51),dest="breadth",type=int, default=0, help="Set the breadth of a crawl. Breadth corresponds to the number of URLs to retrieve from a page, for subsequent scraping.")
    parser.add_argument("--depth",choices=range(0,101),dest="depth",type=int, default=0, help="Set the depth of a crawl. Depth corresponds to the number of times URLs will be extracted from pages (calculated in rounds).")
    parser.add_argument("--separate_store",choices=negative_choice+positive_choice,dest="separate_store",default="False", help="Option to store results under separate directory, rather than under base domain's root directory.")



    arguments=parser.parse_args()

    URL=arguments.url
    delay=arguments.delay
    strategy=arguments.strategy
    crawl=arguments.crawl
    breadth=arguments.breadth
    depth=arguments.depth
    separate_store=arguments.separate_store in positive_choice
    print_msg_arguments(f"Following Strategy {strategy}.")
    searchStart=get_article_name(URL) if separate_store else ""
    print(separate_store)
    visit.append(URL)

    #While list of URLs to traverse is not empty, crawl and scrape for each URL in the list.
    while len(visit)>0:
        url=visit.pop(0)
        print_msg_arguments(url,delay)
        time.sleep(delay)
        if not get_base_URL(url) in visited_robots:
            check_robot(url)
        print_generic_message("Proceed with Scraping!")
        res=fetch(url)
        try:
            if res:
                ##If asked to crawl, get the first "breadth" number of links <a> into a list of lists. When that list reaches length "depth" stop the process of extracting new <a>.
                if crawl in positive_choice and len(crawling)<=depth:
                    buf_extract_crawl=crawl_offline(res,breadth=breadth,URL=url)
                    visit.extend(buf_extract_crawl)
                    crawling.append(buf_extract_crawl)
                    print_success_message(f"Added {len(buf_extract_crawl)} to horizon!")
                print_success_message("Got something!")
                page_title=res.title.text
                page_content=res.body.text

                local_path=check_local_storage_dirs(url)
                if separate_store:
                    local_path=check_article_path(f"Start_{searchStart}/",local_path)
                if local_path:
                    article_path=check_article_path(page_title,local_path)
                    save_resp(res.__str__(),article_path,page_title)
                    print_generic_message("Extracting text!")
                    error=False
                    try:
                        strip(res,article_path,page_title,strategy=strategy)
                    except Exception as E:
                        print_error_message("Error occurred!")
                        error=True
                    if not error:
                        print_success_message("Extraction complete!")

            else:
                print_error_message("Got error! Aborting!")
        except Exception as E:
            print(E)


