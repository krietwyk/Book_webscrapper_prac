import re
import requests
from bs4 import BeautifulSoup

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