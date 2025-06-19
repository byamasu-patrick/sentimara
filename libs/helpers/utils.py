from bs4 import BeautifulSoup

def remove_html_tags(input_string):
    if input_string is None:
        return ""
    soup = BeautifulSoup(input_string, "html.parser")
    clean_text = soup.get_text()
    return clean_text
