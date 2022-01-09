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
from tkinter import font
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from txt_from_page import read_from_page
from next_page import next_page


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
