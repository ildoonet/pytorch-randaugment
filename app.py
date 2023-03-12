import logging
import openai
from hexa import Hexa
from translate import Translator, lang_en, lang_kr
from searchweb import google_serp
from colored import fg, bg, attr

openai.api_key = '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'
DISABLE_HEXA_QUERY = True


logger = logging.getLogger('DDMM')
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


class ChatResponse:
    def __init__(self) -> None:
        pass

class DDMMChat:
    def __init__(self, enable_ref=True):
        logger.debug('DDMMChat init+')
        # self.hexa = Hexa()
        # self.translator = Translator()

        self.enable_ref = enable_ref
        self.history = []
        self.term_history = []
        self.ref = ''
        logger.debug('DDMMChat init-')

    def __call__(self, msg):
        logger.debug(f'DDMMChat call+ {msg}')
        
        # # transla msg to en
        # msg_en = self.translator.translate(msg, lang_en)
        # logger.debug('  msg_en: %s', msg_en)

        # # search-decision
        # pred = self.hexa.generate(msg_en, task="search_decision")[0]
        # logger.debug('  search_decision: %s', pred)

        references = []
        # if pred == "__do-search__" and self.enable_ref:
        # chatGPT
        # msg to search keywords
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages = [
                # {"role": "system", "content": "You are an assistant who searches for the necessary information for the last message. Give me a few good search terms. Just tell me terms, no sentence. If search is not neccessary you think, then just tell me an empty response. Should use same language as the user's message if possible. Each term should be simple but useful for responding to the last message."},
                {"role": "system", "content": """너는 검색 쿼리를 제안하는 어시스턴트이다. 하나의 검색 쿼리를 제안해라. 그냥 단어만 쓰고 불필요한 말은 하지 말라. 검색이 필요없다고 생각하면 그냥 빈 문자열을 써라. 사용자의 메시지와 같은 언어를 사용하면 좋다. 각 단어는 간단하지만, 마지막 메시지에 대한 응답에 유용해야 한다. 히스토리를 보고 쿼리를 구체화할 필요도 있다
예) 강남역 맛집 추천해줘
- 강남역 맛집
answer: ...
고기 먹고 싶어
- 강남역 고기 맛집
answer: ...
4명이 조용히 먹고 싶어. 
- 강남역 고기 맛집 룸
answer: ...
예2) Tesla의 CTO가 누구야?
- Tesla CTO
answer: ...
커리어를 알려줘
- Tesla CTO Career
answer: ...
결혼 했어?
- Tesla CTO Marriage
answer: ...
예3) 고구마가 다이어트에 도움이 되?
- 고구마 다이어트
answer: ...
감자는?
- 감자 다이어트
answer: ...
둘을 비교해줘 
- 고구마 감자 비교
answer: ...
----------"""}
            ] + self.term_history + [
                {"role": "user", "content": f'message: {msg}'}
            ]
        )

        splited_terms = completion['choices'][0]['message']['content'].split('\n')
        keywords = [' '.join(splited_terms)] + splited_terms
        keywords = keywords[:3]     # TODO 
        keywords = [k for i, k in enumerate(keywords) if k not in keywords[:i]]     # remove empty
        logger.debug('  search_query(GPT): %s', keywords)

        self.term_history.append({"role": "user", "content": f'{msg}'})
        self.term_history.append({"role": "assistant", "content": '- ' + ','.join(keywords)})

        if not DISABLE_HEXA_QUERY:
            # HEXA - search-query
            search_q_en = self.hexa.generate(msg_en, task="search_query")[0]
            # transla pred to kr
            search_q_kr = self.translator.translate(search_q_en, lang_kr)
            logger.debug('  search_query(HEXA): %s', search_q_en)
            logger.debug('  search_query(HEXA): %s', search_q_kr)

            # do search
            keywords.extend([search_q_en, search_q_kr])

        for keyword in keywords:
            references.extend(google_serp(keyword)['response'])
        references = [dict(t) for t in {tuple(d.items()) for d in references if d['content']}]      # remove no content (text) 
        references = [dict(t) for t in {tuple(d.items()) for d in references if 'url' in d}]        # dedup
        logger.debug(f'  # references={len(references)}')

        ref = ''
        for r in references:
            logger.debug(f'  ref: {r["url"]}')
            ref += r['content'][:2048]                  # TODO
            ref += '\n-------------------------'
            if len(ref) > 3000:                         # TODO 
                ref = ref[:3000]
        self.ref = ref 
        # else:
        #     ref = self.ref

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the last message. You can use the references and the chat history below. If possible, avoid telling stories that are not in the reference that may not be true."}
            ] + [
                {"role": "system", "content": '[레퍼런스 자료]\n\n' + ref}         # maximum context length is 4097 tokens
            ] + self.history[-4:] + [
                {"role": "user", "content": msg}
            ]
        )
        response = completion['choices'][0]['message']['content']  

        self.history.append({"role": "user", "content": msg})
        self.history.append({"role": "assistant", "content": response})
        self.term_history.append({"role": "assistant", "content": 'answer: ' + response})

        return response


if __name__ == '__main__':
    # argparse
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable_ref', action='store_true')
    args = parser.parse_args()

    chat = DDMMChat(enable_ref=not args.disable_ref)

    while True:
        c = input(f'{fg(196)}User: ')
        print(attr(0), end='')
        print(fg(2), chat(c), attr(0))