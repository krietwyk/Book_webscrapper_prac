"""
A webscraping GUI created as a tutorial for GUI creation, webscraping, text/str
analysis and basic URL funcitons. The GUI scrapes pages from websites with
entire books. The url for the first pages is provided, the book text is 
extracted from the page and the link to the next page is identified. The text
from the next page and link to the subsequent page is likewise read until the
end of the book is reached. A simple filter is employed to remove any footers
and unwanted spacing.

The GUI was designed as a simple learning excercise and should be not employed
to extract text from webpages without appropriate permissions!
"""

import time
import tkinter as tk
import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from tkinter import font
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog

def full_txt_get(url):
    """
    Webscrapes the text of the first page of a book and checks if there are 
    more pages. If so it continues to collect the text from each page until 
    the last page is reached. The text is filtered for a footer.
    """
    pg = 1
    print(pg)
    full_txt = read_from_page(url)
    href = url
    while len(href) > 0: # Loops until it stops finding next pages
        pg += 1
        print(pg)
        # Identify the next link from the text 
        href_old = href
        href, last_pg_chk = next_page(href, pg)
        # check if old and new href are the same or if, new if the page is '#'
        # if new, get txt from this page and go to the next url 
        if last_pg_chk or href == href_old: 
            break
        page_txt = read_from_page(href)
        full_txt += page_txt
        # Store pages 2 and 3 to later check for repeated footer
        if pg == 2:
            text_2 = page_txt
        elif pg == 3:
            text_3 = page_txt
    # Compare if the end of the text from pages 2 and 3, if the same, check more 
    substr_ind = -5    
    substr = text_2[substr_ind:]
    while substr in text_3:
        substr_ind += -1
        substr = text_2[substr_ind:]    
    # This might include additional text not other pages so just the text a little
    substr_cnt = 0
    for i in range(1, 15):
        for j in range(15):
            test_val = full_txt.count(substr[substr_ind+i:])
            test_val2 = full_txt.count(substr[i:-j])
            if test_val > substr_cnt and j == 0:
                substr_cnt = test_val
                substr_ind_rf = [substr_ind+i, -j]
            elif test_val2 > substr_cnt and j > 0:
                substr_cnt = test_val2
                substr_ind_rf = [substr_ind+i, -j]
    # Search the full text and remove the refined substring 
    if substr_cnt > 0 and substr_ind_rf[1] == 0:
        full_txt = full_txt.replace(substr[substr_ind_rf[0]:],"")
    elif substr_cnt > 0:
        full_txt = full_txt.replace(substr[substr_ind_rf[0]:substr_ind_rf[1]],"")
    return full_txt

def read_from_page(url, cutoff=0.5):
    """ The book text is expected to reside within a div class so the url is 
    accessed and the position of the opening and closing of div classes are 
    ascertained and the ranking or degree of nesting is determined. If this 
    fails a 2nd approach of defining the div class using beautiful soup is 
    employed. Ranking prove inadequate for identifying only the page text 
    without including extra webpage junk. Instead the text div class is 
    chosen to be a large section and some cutoff fraction of the largest class.
    A classes are then removed because they may be links within the text.
    """
    r = requests.get(url)
    r_html = r.text
    # Text pattern for div class openings and closing in html
    div_o = '<div|< div|<  div'
    div_c = '</div|</ div|< /div|< / div'
    # Locations in html of inner positions 
    div_o_st = [i.start() for i in re.finditer(div_o, r_html)]  
    div_c_st = [i.start() for i in re.finditer(div_c, r_html)]
    try: # This method provides rank which proved not to be so useful
        div_o_st_cl = div_o_st.copy()
        reg_rank, reg_val= [0]*len(div_c_st), [0]*len(div_c_st)
        # Find index of open for each close brackets: id max open position in
        # txt less than each div_c_st and remove from div_o_st clone 
        for loop_ind, div_c_st_val in enumerate(div_c_st):
            reg_ind = max(
                [div_o_st_ind for div_o_st_ind, div_o_st_val in 
                 enumerate(div_o_st_cl) if div_o_st_val < div_c_st_val])
            reg_val[loop_ind] = div_o_st_cl[reg_ind]
            reg_rank[loop_ind] = reg_ind # Nest ranking
            div_o_st_cl.pop(reg_ind)     
        # Length of each div section of txt
        reg_len = [len(r_html[reg_val[i]:c_st]) 
                   for i, c_st in enumerate(div_c_st)] 
        # Smallest div section greater than 50% largest section
        # Idea: largest to contain all text but has minimal junk
        sub_ind = min(
            {j: i for i, j in enumerate(reg_len) 
             if j-cutoff*max(reg_len) > 0}.items())[1]
        soup = BeautifulSoup(r_html[reg_val[sub_ind]:div_c_st[sub_ind]], 
                             features="lxml") 
    except: # if the previous approach fails use beautiful soup
        # Calculate string size of each div class section
        soup = BeautifulSoup(r_html, features="lxml")
        txt_extract = soup.find_all('div')        
        reg_len = [len(element.get_text()) for element in txt_extract]
        # Smallest div section greater than cutoff multiplier of largest
        sub_ind = min(
            {j: i for i, j in enumerate(reg_len) 
             if j-cutoff*max(reg_len) > 0}.items())[1]        
        soup = txt_extract[sub_ind] 
    # Remove any 'a' classes (often prev and next button/text)
    for tag in soup('a'):
        tag.decompose()
    # Clean up text to remove unnecessary spacing
    page_txt = soup.get_text(separator=u"\n")
    page_txt = re.sub("[\t]*", "", page_txt)
    page_txt = "".join(
        [s for s in page_txt.strip().splitlines(True) if s.strip()])
    return page_txt

def next_page(url, pg=2):
    """
    Search through text on URL to identify the link to the next page. If this
    fails or if the link to the next page is simply '#', assume last page.
    """
    r = requests.get(url)
    r_html = r.text
    soup = BeautifulSoup(r_html, features="lxml")
    links = soup.find_all("a")
    for i in links: # Identify next page link using 3 methods
        try: # 1. Link may just be the page number and nothing else
            if re.compile(str(pg)).fullmatch(
                    re.sub('[^A-Za-z0-9]+', '', i.string)):
                herf_next = i
        except:
            pass
        try: # 2. Link is nextchapter
            if re.compile("nextchapter").match(
                    re.sub('[^A-Za-z0-9]+', '', i.string.lower)):
                herf_next = i
            elif re.compile("next chapter").match(
                    re.sub('[^A-Za-z0-9]+', '', i.string.lower)):
                herf_next = i
            elif re.compile("next_chapter").match(
                    re.sub('[^A-Za-z0-9]+', '', i.string.lower)):
                herf_next = i
        except:
            pass
        try: # 3. Check if it includes the word 'next'
            if 'next' in str(i.get_text).lower():
                herf_next = i
        except:
            pass
    # Form a complete URL 
    try: # Assume page was found if not an UnboundLocalError will occur
        href = herf_next.attrs.get("href") 
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        last_pg_chk = herf_next.attrs.get("href")  == '#'
    except UnboundLocalError:
        last_pg_chk = True
        href = "NaN" # Placeholder 
    return href, last_pg_chk

def btn_load_cmd():
    """
    Get url from entryfield, read text from page, insert text into text field
    and provide the link to the next page to verify it is appropriate
    """
    url = urlfld.get()
    pg_txt = read_from_page(url)
    text_disp.delete("1.0", tk.END)
    text_disp.insert("1.0", pg_txt)
    href, last_pg_chk = next_page(url)
    urlfld_next.configure(state='normal')
    urlfld_next.delete(0, tk.END)
    urlfld_next.insert(tk.END, href)
    urlfld_next.configure(state='disabled')
    print(url)
    return url
    
def btn_full_txt_cmd():
    """
    Gets the text for the book and places it into the text field. It outputs
    the curation duration into the status text box.
    """
    t_st = time.time()
    url = urlfld.get()
    status.configure(state='normal')
    status.configure(state='disabled')
    full_txt = full_txt_get(url)
    text_disp.delete("1.0", tk.END)
    text_disp.insert("1.0", full_txt)
    status.configure(state='normal')
    status.insert(tk.END, "Completed curation in %d s\n" % (time.time()-t_st))
    status.configure(state='disabled')
    return full_txt
    
def validate(*args):
    # Checks if url text entry is populated and enable/disable get text button.
    if url_text.get():
        btn_full_txt.config(state='normal')
    else:
        btn_full_txt.config(state='disabled')
        
def file_save():
    # Uses a dialogue box to save the text in the text field as a txt.
    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    if filename is None: # asksaveasfile return `None` if dialog closed
        return
    text2save = text_disp.get('1.0', tk.END) 
    print(filename)
    with open(filename, "wb") as f:
        f.write(text2save.encode('utf8'))

root = tk.Tk()
root.title("Book scraper tutorial")
root.geometry("850x820+500+200")

url_text = tk.StringVar()

lbl = tk.Label(root, text="Book page 1 URL:", fg='black',
                    font=("Helvetica", 16))
lbl.place(x=60, y=50)

urlfld = tk.Entry(root, text="url", bd=3, width=100, textvariable=url_text)
urlfld.place(x=60, y=80)
urlfld.bind("<Return>", btn_load_cmd) 

url_text.trace("w", validate) 

btn_load = tk.Button(root, text = "Get 1st page", command=btn_load_cmd)
btn_load.place(x=60, y=110)

text_disp = ScrolledText(root, height=20, width=75, wrap="word")
text_disp.place(x=60, y=150)

lbl_2 = tk.Label(root, text="Next page:", fg='black',
                    font=("Helvetica", 12))
lbl_2.place(x=60, y=480)

urlfld_next = tk.Entry(root, text="Next page", bd=3, width=100)
urlfld_next.place(x=60, y=510)
urlfld_next.config(state='disabled')

btn_full_txt_font = font.Font(size=16, weight='bold')
btn_full_txt = tk.Button(root, height = 2, font=btn_full_txt_font,
                         bg='#0052cc', fg='#FFFFFF',
                         text = "Get full text", command=btn_full_txt_cmd)
btn_full_txt.place(x=60, y=540)
btn_full_txt.config(state='disabled')

status = tk.Text(root, bd=4, height=3, width=57)
status.place(x=200, y=540)
status.configure(state='disabled')

btn_save = tk.Button(root, text = "Save", font=("Helvetica", 14),
                     command=file_save)
btn_save.place(x=380, y=610)

root.mainloop()
