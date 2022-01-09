# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 15:47:29 2021

@author: Kevin
"""

# import urllib.request
import time
import re 
# import webbrowser 
import requests
from bs4 import BeautifulSoup
# import numpy as np
from urllib.parse import urlparse, urljoin

## google - site:http://novelfreereadonline.com [bookname]
## https://onlinereadfreenovel.com/
## set url to contents page
t_st = time.time()


def txt_from_page(url):
    r = requests.get(url)
    r_html = r.text

    soup = BeautifulSoup(r_html, features="lxml")
    # body = soup.find('body')
    # mydivs = body.findAll('div')
    
    pattern = '< *div'
    # patternc = '<div *class|< *div *class'
    patternn= '</ div|< /div|< / div|</div'
    # patternnc = '</ *div *class|</ *div *class|< */ *div *class'
    
    # print(len(re.findall(patternc, r_html)))
    # print(len(re.findall(patternnc, r_html)))
    
    div_st = [] 
    divn_st = []
    pos = 0
    while pos > -1:
        try:
            div_st.append(re.search(pattern, r_html[pos:]).span()[0]+pos+1)
            pos = div_st[-1]
        except: 
            break
    
    pos = 0
    while pos > -1:
        try:
            divn_st.append(re.search(patternn, r_html[pos:]).span()[0]+pos+1)
            pos = divn_st[-1]
        except: 
            break
        
    div_st = [i-1 for i in div_st]
    # divn_st = [i+6 for i in divn_st]
    
#Identify which open brack correspond to which close brackets
    # reg defines this but sect[i][2] define the rank, so the largest 
    # reg with the highest rank should be the body text
    
    i = 0
    j = 0
    k = 0
    z = 0
    sect = []
    reg = []
    op_count = [*range(len(div_st))]
    cl_count = [*range(len(divn_st))]
    
    while k > 0 or i < len(div_st):
        z += 1
        try:
            if div_st[i] < divn_st[j]:
                i += 1
                k += 1
            elif divn_st[j] < div_st[i]:
                k += -1
                reg.append([op_count[k], cl_count[j]])
                del op_count[k]
                sect.append([i, j, k])
                j += 1
    
        except:
            k += -1
            reg.append([op_count[k], cl_count[j]])
            # del op_count[k]
            sect.append([i, j, k])
            j += 1
    
        # print(z,i,j,k)
# Identify the largest region with highest rank and make it soup
    
    # l_reg = -1
    # ind_reg = -1
    # for i in range(len(reg)):
    #     if sect[i][2] == max(sect[:][2]):
    #         if len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]]) > l_reg:
    #             l_reg = len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]])
    #             ind_reg = i
    #             # print(len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]]))
    # # print(r_html[div_st[reg[ind_reg][0]]:divn_st[reg[ind_reg][1]]]) 
    
# Identify the largest segment, then pick a segment that is smaller 
# but similar in size
    
    s_reg = []    
    for i in range(len(reg)):
        s_reg.append(len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]]))
        # print(s_reg)
    # ind_reg = 
    max(s_reg)
    temp = [temp2-0.5*max(s_reg) for temp2 in s_reg]
    sub_reg = max(s_reg)
    z = -1
    for i in temp:
        z += 1
        if i > 0 and i < sub_reg:
            sub_reg = i
            ind_sub = z
    
    ind_reg = ind_sub              
    
    soup = BeautifulSoup(r_html[div_st[reg[ind_reg][0]]:divn_st[reg[ind_reg][1]]], features="lxml")   
    # Remove a class (often prev and next button/text)
    for tag in soup('a'):
        tag.decompose()
    # soup.find('a').decompose()
    page_txt = soup.get_text(separator=u"\n")
    page_txt = re.sub("\n\n*", "\n", page_txt) 
    page_txt = re.sub("\n[\t]*\n", "\n", page_txt)
    # Remove line breaks
    page_txt = "".join([s for s in page_txt.strip().splitlines(True) if s.strip()])
    return page_txt 

#%%
def txt_from_page2(url):
    r = requests.get(url)
    r_html = r.text
    soup = BeautifulSoup(r_html, features="lxml")
    txt_extract = soup.find_all('div')
    
    l_reg = -1
    ind_reg = -1
    z = -1
    for element in txt_extract:
        z += 1
        if len(element.get_text()) > l_reg:
            l_reg = len(element.get_text())
            ind_reg = z
            # print(l_reg)
            # print(ind_reg)
    
    page_txt = txt_extract[ind_reg].get_text(separator=u"\n")
    page_txt = re.sub("\n\n*", "\n", page_txt)        
    page_txt = re.sub("\n[\t]*\n", "\n", page_txt)
    page_txt = "".join([s for s in page_txt.strip().splitlines(True) if s.strip()])
    return page_txt
#%% Identify links

nam = "Chapterhouse Dune"
url = 'https://www.free-best-books.com/fantasy/3957.html'
url = 'https://novelfreereadonline.com/feet-of-clay/chapter-1-88124'
# url = 'https://onlinereadfreenovel.com/douglas-adams/31423-dirk_gentlys_holistic_detective_agency.html'
# url = 'http://readonlinefreebook.com/dune/c-one'
# url = 'http://readonlinefreebook.com/dune-messiah/prologue'
# url = 'http://readonlinefreebook.com/children-of-dune/c-one'
# url = 'http://readonlinefreebook.com/god-emperor-of-dune/c-one'
# url = 'http://readonlinefreebook.com/heretics-of-dune/c-one'
url = 'http://readonlinefreebook.com/chapterhouse-dune/c-one'

domain_name = urlparse(url).netloc
page_txt = ''
full_txt = ''
try:
    page_txt = txt_from_page(url)
except:
    page_txt = txt_from_page2(url)
full_txt += page_txt

href = url
z=0
pg = 1
while len(href) > 0:
    z += 1
    pg += 1
    print(z)
# Identify the next link
    href_old = href
    r = requests.get(href)
    r_html = r.text
    soup = BeautifulSoup(r_html, features="lxml")
    
    links = soup.find_all("a")
    for i in links:
        try:
            if re.compile(str(pg)).fullmatch(re.sub('[^A-Za-z0-9]+', '', i.string)):
                temp = i
        except:
            pass
        try:
            if 'next' in str(i.get_text).lower():
                temp = i
        except:
            pass
    try:
        if len(soup.find_all("a", string="Next")) > 0:
            temp = soup.find_all("a", string="Next") 
        elif len(soup.find_all("a", string="next")) > 0:
            temp = soup.find_all("a", string="next")
        temp = temp[0]
    except:
        pass
# trying to find out which works better
    # for i in links:
    #     try:
    #         if "next" in i.string.lower() and len(i.string) < 7: 
    #             temp = i
    #         elif re.compile("nextchapter").match(re.sub('[^A-Za-z0-9]+', '', i.string.lower)):
    #             temp = i
    #         elif re.compile(str(pg)).fullmatch(re.sub('[^A-Za-z0-9]+', '', i.string)):
    #             temp = i
    #     except:
    #         pass
       
   
    # print(temp)   
    # check if old and new href are the same or if new is #
    # if new, get txt from this page and go to the next     
    href = temp.attrs.get("href") 
    
    # href = temp[0].attrs.get("href")
    href = urljoin(url, href)
    parsed_href = urlparse(href)
    href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
    # print(href)
    
    if temp.attrs.get("href")  == '#' or href == href_old: # Incase of '#'
        break       
    try:
        page_txt = txt_from_page(href)
    except:
        page_txt = txt_from_page2(href)
    # page_txt = txt_from_page2(href) 
    full_txt += page_txt


f= open("C:\\Users\\Kevin\\Documents\\"+nam+".txt","w+", errors="ignore")
f.write(full_txt)
f.close()

    
print(time.time()-t_st)

#%%
asfasf

#%%

links = soup.find_all("a")
for i in links:
    try:
        if len(soup.findAll("a", string="Next")) > 0:
            temp = soup.findAll("a", string="Next") 
        elif len(soup.findAll("a", string="next")) > 0:
            temp = soup.findAll("a", string="next")
        elif re.compile(str(pg)).match(re.sub('[^A-Za-z0-9]+', '', i.string)):
            temp = i
    except:
        pass
    # try:
    #     if 'next' in str(i.get_text).lower():
    #             temp = i
    # except:
    #     pass
print(temp)

 
#%%
sgdsg

#%%
r = requests.get(url)
r_html = r.text

soup = BeautifulSoup(r_html, features="lxml")
# body = soup.find('body')
# mydivs = body.findAll('div')

pattern = '< *div'
# patternc = '<div *class|< *div *class'
patternn= '</ div|< /div|< / div|</div'
# patternnc = '</ *div *class|</ *div *class|< */ *div *class'

# print(len(re.findall(patternc, r_html)))
# print(len(re.findall(patternnc, r_html)))
#%%

div_st = [] 
divn_st = []
pos = 0
while pos > -1:
    try:
        div_st.append(re.search(pattern, r_html[pos:]).span()[0]+pos+1)
        pos = div_st[-1]
    except: 
        break

pos = 0
while pos > -1:
    try:
        divn_st.append(re.search(patternn, r_html[pos:]).span()[0]+pos+1)
        pos = divn_st[-1]
    except: 
        break
    
div_st = [i-1 for i in div_st]
divn_st = [i+6 for i in divn_st]

#%% Identify which open brack correspond to which close brackets
# reg defines this but sect[i][2] define the rank, so the largest 
# reg with the highest rank should be the body text

i = 0
j = 0
k = 0
z = 0
sect = []
reg = []
op_count = [*range(len(div_st))]
cl_count = [*range(len(divn_st))]

while k > 0 or i < len(div_st):
    z += 1
    try:
        if div_st[i] < divn_st[j]:
            i += 1
            k += 1
        elif divn_st[j] < div_st[i]:
            k += -1
            reg.append([op_count[k], cl_count[j]])
            del op_count[k]
            sect.append([i, j, k])
            j += 1

    except:
        k += -1
        reg.append([op_count[k], cl_count[j]])
        # del op_count[k]
        sect.append([i, j, k])
        j += 1

    # print(z,i,j,k)
    
#%% Identify the largest region with highest rank and make it soup

l_reg = -1
ind_reg = -1
for i in range(len(reg)):
    if sect[i][2] == max(sect[:][2]):
        if len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]]) > l_reg:
            l_reg = len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]])
            ind_reg = i
            # print(len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]]))
# print(r_html[div_st[reg[ind_reg][0]]:divn_st[reg[ind_reg][1]]]) 

soup = BeautifulSoup(r_html[div_st[reg[ind_reg][0]]:divn_st[reg[ind_reg][1]]], features="lxml")   

page_txt = soup.get_text(separator=u"\n")

#%%


to_remove = soup.find_all('div', {'id': "textToRead"})

for element in to_remove:
    print(len(element))
    print(element)
    print('***********************************')








#%%














# soup = BeautifulSoup(requests.get(url).content, "html.parser")

a_tag = soup.findAll("a")[28] # temp


for a_tag in soup.findAll("a"):
    href = a_tag.attrs.get("href")
    if href == "" or href is None:
        # href empty tag
        continue
    
    href = urljoin(url, href)
    parsed_href = urlparse(href)
    # remove URL GET parameters, URL fragments, etc.
    href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

#%%
sgdsg

#%%

# f= open("C:\\Users\\Kevin\\Documents\\"+nam+".txt","w+", errors="ignore")
# f.write(full_txt)
# f.close()

internal_urls = set()
external_urls = set()

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    
urls = set()
# domain name of the URL without the protocol
urlparse(url).netloc
domain_name = urlparse(url).netloc
soup = BeautifulSoup(requests.get(url).content, "html.parser")




for a_tag in soup.findAll("a"):
    href = a_tag.attrs.get("href")
    if href == "" or href is None:
        # href empty tag
        continue
    
    href = urljoin(url, href)
    parsed_href = urlparse(href)
    # remove URL GET parameters, URL fragments, etc.
    href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

    if not is_valid(href):
        # not a valid URL
        continue
    if href in internal_urls:
        # already in the set
        continue
    if domain_name not in href:
        # external link
        if href not in external_urls:
            # print(f"{GRAY}[!] External link: {href}{RESET}")
            external_urls.add(href)
        continue
    # print(f"Internal link: {href}{RESET}")
    urls.add(href)
    internal_urls.add(href)



     
#%%
for i in range(len(reg)):
    print(reg[i])
    print(i)
    # print(pos[reg[i][0]])
    # if reg[i][0] == reg[i][1]:
    if sect[i][2] == max(sect[:][2]):
        print('**************************************************')
        print(len(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]]))
        print(r_html[div_st[reg[i][0]]:divn_st[reg[i][1]]])       
#%%








i = 0
pos_st = []
pos_fi = []
while div_st[i] < divn_st[-(i+1)]:
    pos_st.append(div_st[i]) 
    pos_fi.append(divn_st[-(i+1)])
    i += 1
print(pos_st)




#%%
i=8
print(r_html[pos_st[i]-1:pos_fi[i]-1])
soup = BeautifulSoup(r_html[pos_st[i]-1:pos_fi[i]-1])
#%%
for i in range(len(pos_st)-1):
    print(len(r_html[pos_st[i]-1:pos_fi[i]-1]) - 
          len(r_html[pos_st[i+1]-1:pos_fi[i-1]-1]))

 #%%
 

count_ = []
count2_ = []
count2 = 0
for i in range(len(div_st)-1):
    count = 0
    while div_st[i+1] < divn_st[i]:
        i=i+1
        count += 1
        count2 += 1
    # elif div_st[i+1] > divn_st[i]:
    #     count2 += -1
    #     count += -1
        # print(i)
    count_.append(count)
    count2_.append(count2)
print(count_)
print(count2_)

#%%
# num_st = np.array([])
# numn_st = np.array([])
# for i in div_st:
#     num_st = np.append(num_st, float(i))

# for i in divn_st:
#     numn_st = np.append(numn_st, float(i))

# temp = numn_st - num_st[1]    

#%%   
# j = 0
# count_ = []
# for i in range(len(div_st)):
#     count = 0
#     j = i
#     try:
#         while divn_st[j] > div_st[i]:
#             count += 1
#             i += 1
#             print(count)
#         count_.append(count)
#     except:
#         count_.append(1)
# print(count_)
    
#%%
div_sizes=[]
for div in mydivs:
    div_sizes.append(len(div.text))
div_max = max(div_sizes)
div_max_ind = div_sizes.index(div_max)
r_text = mydivs[div_max_ind].text


#%%


try: 
    temp = re.search('/[0-9]+/',url).span()
except:
    temp = re.search('/[a-zA-z0-9]+-[a-zA-z0-9]+/',url).span()
    tempo = re.search('"pagination"',r_html).span()[0]
    case = 1
#     fin = r_html[tempo:].find('</ul>')
else:
    tempo = re.search('id="listchapter"',r_html).span()[0]
fin = r_html[tempo:].find('</ul>')
fin += tempo 
sta = temp[0]
stp = temp[1]
nam = url[stp:]
base_url = url[0:sta]
# r_html[tempo:tempo+fin] ## contains all the urls

u = 1
urllst = []
while u>0:
    v = r_html[tempo:fin].find('href="')
    u=-1
    if v >0:
        kl = re.search('href="[0-9a-zA-Z/_,-]+"',r_html[tempo:fin]).span()
        urllst.append(r_html[tempo+kl[0]+1+len('ref="'):tempo+kl[1]-1])
        tempo += kl[1]
        u=kl[0]
        urltemp = base_url+urllst[-1]
        print(urltemp)
        q = requests.get(urltemp)
        q_html = q.text
        st = re.search('<div class="content.?-c',q_html).span()[0]
        st += re.search('>',q_html[st:]).span()[0]+1
        q_html=q_html[st:]
        x = q_html[:].find('</div>')
#         print(x)
        y = q_html[:x].find('<div')
#         print(y)
        while y > 0:
            q_html = q_html[:y]+q_html[x+len('</div>'):]
            x = q_html[:].find('</div>')
            y = q_html[:x].find('<div') 
        fi = q_html[:].find('</div>')
    
    
    
#         if case == 0:
# #             st1 = re.search('<p>',q_html[st:]).span()[0] # isn't working for feet of clay
# #             st1 = re.search('>',q_html[st:]).span()[0]+1
# #             st1 = re.search('<div>',q_html[st:]).span()[0]
#             fi = q_html[st:].find('</p>')
#         else:
# #             st1 = re.search('</a>',q_html[st:]).span()[0]
#             fi = q_html[st:].find('</div>')
#             print("case_1",fi)
            
        
        
        soup = BeautifulSoup(q_html[:fi],)
        full_txt += soup.get_text(separator="\n")


f= open("C:\\Users\\Kevin\\Documents\\"+nam+".txt","w+", errors="ignore")
f.write(full_txt)
f.close()