from request_boost import boosted_requests
import justext
import html
from serpapi import GoogleSearch
import logging
from colored import fg, bg, attr
import trafilatura

_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


logger = logging.getLogger('SEARCH')
logger.setLevel(logging.DEBUG)

class CustomFormatter(logging.Formatter):
    grey = fg(240)
    yellow = fg(184)
    red = fg(160)
    bold_red = bg(196)
    reset = attr(0)
    format = "[%(asctime)s][%(name)s][%(levelname)s](%(filename)s:%(lineno)d) %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())
logger.addHandler(stream_handler)



def get_htmls(links):
    try:
        # logger.debug(f'get_htmls {links}')
        texts = boosted_requests(links, headers=[_headers] * len(links), timeout=5, max_tries=2, parse_json=False)
    except Exception as e:
        print(f'get_htmls {str(e)} ... {links}')
        return []
    texts = list(filter(None, texts))
    return texts


def get_content(text):
    # title
    try:
        title = text[text.find('<title>') + 7 : text.find('</title>')].replace('\n', ' ')
        title = html.unescape(title).strip()
    except:
        title = ''

    # paragraphs = justext.justext(text, justext.get_stoplist("Korean"))
    # # remove all paragraphs that are not plain text
    # contents = []
    # for paragraph in paragraphs:
    #     if not paragraph.is_boilerplate:
    #         contents.append(paragraph.text.replace('\n', ' '))
    content = trafilatura.extract(text)
    return title, content


def google_serp(query):
    # https://serpapi.com/search-api
    gsearch = GoogleSearch({
        "q": query, 
        # "tbm": "isch", 
        "gl": "us", "safe": "active",
        "api_key": "299af8d20c391660a53e49691eb092d7254e397db362d3d074f42d028d852c9b"
    })
    
    import json
    pages = gsearch.get_dict().get('organic_results', [])
    logger.debug('#pages: %d', len(pages))
                 
    links = [p['link'] for p in pages]
    htmls = get_htmls(links)
    results = {'response': []}
    for p, text in zip(pages, htmls):
        title, link = p['title'], p['link']
        title, content = get_content(text)
        # if content:
        #     logger.debug('  ' + link)
        results['response'].append({'url': link, 'title': title, 'content': content})

    return results


if __name__ == '__main__':
    # print(google_serp('프링글스'))
    d = get_htmls(['https://www.mangoplate.com/search/%EC%84%B8%EA%B3%A1%EB%8F%99'])
    print(type(d))
    # with open('test.html', 'w') as w:
    #     w.write(d[0])
    print(get_content(d[0]))