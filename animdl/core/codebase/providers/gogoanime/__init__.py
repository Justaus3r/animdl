from functools import partial

import lxml.html as htmlparser
import regex

from ....config import GOGOANIME
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(
    GOGOANIME,
    extra_regex=r"/(?:(?P<episode_anime_slug>[^&?/]+)-episode-[\d-]+|category/(?P<anime_slug>[^&?/]+))",
)

ANIME_ID_REGEX = regex.compile(r'<input.+?value="(\d+)" id="movie_id"')
EPISODE_LOAD_AJAX = "https://ajax.gogo-load.com/ajax/load-list-episode"


def get_episode_list(session, anime_id):
    """
    Fetch all the episodes' url from GogoAnime using.
    """
    episode_page = session.get(
        EPISODE_LOAD_AJAX,
        params={
            "ep_start": "0",
            "ep_end": "100000",
            "id": anime_id,
        },
    )
    genexp = iter(
        htmlparser.fromstring(episode_page.text).cssselect(
            'a[class=""] , a[class=""]  > div.name'
        )
    )

    for (a, div) in zip(genexp, genexp):
        yield float(div.text_content().split(" ")[1]), GOGOANIME + a.get(
            "href"
        ).strip(),


def get_quality(url_text):
    match = regex.search(r"(\d+)P", url_text)
    if not match:
        return None
    return int(match.group(1))


def get_embed_page(session, episode_url):
    content_parsed = htmlparser.fromstring(session.get(episode_url).text)
    return "https:{}".format(content_parsed.cssselect("iframe")[0].get("src"))


def fetcher(session, url, check, match):

    if match.group("episode_anime_slug"):
        url = "{}category/{}".format(GOGOANIME, match.group("episode_anime_slug"))

    content_id = ANIME_ID_REGEX.search(session.get(url).text).group(1)

    for episode, episode_page in reversed(list(get_episode_list(session, content_id))):
        if check(episode):
            yield partial(
                lambda e: [
                    {
                        "stream_url": get_embed_page(session, e),
                        "further_extraction": ("gogoplay", {}),
                    }
                ],
                episode_page,
            ), episode
