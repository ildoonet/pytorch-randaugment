# coding:utf-8
"""
Name       : __init__
Author     : Kuldeep Singh Sidhu
GitHub     : https://github.com/singhsidhukuldeep
Description:
"""

import json
import queue
from datetime import datetime
from threading import Thread
from urllib import parse, request


def boosted_requests(
    urls,
    no_workers=32,
    max_tries=1,
    timeout=5,
    headers=None,
    data=None,
    verbose=True,
    parse_json=True,
):
    """
    Get data from APIs in parallel by creating workers that process in the background
    :param urls: list of URLS
    :param no_workers: maximum number of parallel processes {Default::32}
    :param max_tries: Maximum number of tries before failing for a specific URL {Default::5}
    :param timeout: Waiting time per request {Default::10}
    :param headers: Headers if any for the URL requests
    :param data: data if any for the URL requests (Wherever not None a POST request is made)
    :param verbose: Show progress [True or False] {Default::True}
    :param parse_json: Parse response to json [True or False] {Default::True}
    :return: List of response for each API (order is maintained)
    """
    start = datetime.now()

    def _printer(inp, end=""):
        # print(
        #     f"\r::{(datetime.now() - start).total_seconds():.2f} seconds::",
        #     str(inp),
        #     end=end,
        # )
        pass

    class GetRequestWorker(Thread):
        def __init__(
            self, request_queue, max_tries=5, timeout=10, verbose=True, parse_json=True
        ):
            """
            Workers that can pull data in the background
            :param request_queue: queue of the dict containing the URLs
            :param max_tries: Maximum number of tries before failing for a specific URL
            :param timeout: Waiting time per request
            :param verbose: Show progress [True or False]
            :param parse_json: Parse response to json [True or False]
            """
            Thread.__init__(self)
            self.queue = request_queue
            self.results = {}
            self.max_tries = max_tries
            self.timeout = timeout
            self.verbose = verbose
            self.parse_json = parse_json

        def run(self):
            while True:
                if self.verbose:
                    _printer(f">> {self.queue.qsize()} requests left", end="")
                if self.queue.qsize() == 0:
                    break
                else:
                    is_error = False
                    content = self.queue.get()
                    url = content["url"]
                    header = content["header"]
                    num_tries = content["retry"]
                    data = content["data"]
                    loc = content["loc"]
                    # assert (
                    #     num_tries < self.max_tries
                    # ), f"Maximum number of attempts reached {self.max_tries} for {content}"

                    if num_tries >= self.max_tries:
                        # 성공으로 처리함, 빈 문서
                        self.results[loc] = ''
                        self.queue.task_done()
                        is_error = True

                if is_error:
                    continue
                    
                try:
                    if data is not None:
                        data = parse.urlencode(data).encode()
                        _request = request.Request(url, data=data)
                    else:
                        _request = request.Request(url)
                    for k, v in header.items():
                        _request.add_header(k, v)
                    response = request.urlopen(_request, timeout=self.timeout)
                except Exception as exp:
                    content["retry"] += 1
                    self.queue.put(content)
                    continue

                if response.getcode() == 200:
                    data = response.read()
                    encoding = response.info().get_content_charset("utf-8")
                    try:
                        decoded_data = data.decode(encoding)
                    except UnicodeDecodeError as e:
                        print(e, url, encoding)
                        decoded_data = ''
                    self.results[loc] = (
                        json.loads(decoded_data) if self.parse_json else decoded_data
                    )
                    self.queue.task_done()
                else:
                    content["retry"] += 1
                    self.queue.put(content)

    if headers is None:
        headers = [{} for _ in range(len(urls))]
    if data is None:
        data = [None for _ in range(len(urls))]

    assert len(headers) == len(
        urls
    ), "Length of headers and urls need to be same OR headers needs to be None"
    assert len(data) == len(
        urls
    ), "Length of data and urls need to be same OR data needs to be None (in case of GET)"

    url_q = queue.Queue()
    for i in range(len(urls)):
        url_q.put(
            {
                "url": urls[i],
                "retry": 0,
                "header": headers[i],
                "loc": i,
                "data": data[i],
            }
        )

    workers = []

    for _ in range(min(url_q.qsize(), no_workers)):
        worker = GetRequestWorker(
            url_q,
            max_tries=max_tries,
            timeout=timeout,
            verbose=verbose,
            parse_json=parse_json,
        )
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()

    ret = {}
    for worker in workers:
        ret.update(worker.results)
    if verbose:
        _printer(f">> DONE")
    return [ret[_] for _ in range(len(urls))]