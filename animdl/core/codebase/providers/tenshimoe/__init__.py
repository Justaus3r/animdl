import re

from functools import partial

import lxml.html as htmlparser

from ....config import TENSHI
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(
    TENSHI, extra_regex=r'/anime/([^?&/]+)')


def extract_urls(session, episode_page):
    episode_page_content = session.get(episode_page)
    embed_page = (htmlparser.fromstring(episode_page_content.text).cssselect('iframe') or [{}])[0].get('src')
    streams_page = session.get(embed_page, headers={'referer': episode_page})
    yield from ({'quality': int(_.group(2)), 'stream_url': _.group(1)} for _ in re.finditer(r"src: '(.+?)'.+?size: (\d+)", streams_page.text, flags=re.S))

def fetcher(session, url, check):

    url = REGEX.search(url).group(0)

    episode_list_page = session.get(url)
    count = int(htmlparser.fromstring(episode_list_page.text).cssselect('span.badge')[0].text_content())

    for episode in range(1, count + 1):
        if check(episode):
            yield partial(lambda c: [*extract_urls(session, c)], "{}/{:d}".format(url, episode)), episode
