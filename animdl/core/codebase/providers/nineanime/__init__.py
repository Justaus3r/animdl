from ....config import NINEANIME
from ...helper import construct_site_based_regex
from .. import crunchyroll, gogoanime, twistmoe, zoro

REGEX = construct_site_based_regex(
    NINEANIME, extra_regex=r"/watch/[^&?/]+\.(?P<slug>[^&?/]+)"
)

ALTERNATIVES = "https://animixplay.to/assets/rec/{}.json"
SLUG_SEARCH = "https://raw.githubusercontent.com/MALSync/MAL-Sync-Backup/master/data/pages/9anime/{}.json"


def safe_iter(session, check, provider, url):
    match = provider.REGEX.search(url)

    if not match:
        return None, None

    genexp = provider.fetcher(session, url, check, match)

    try:
        return next(genexp), genexp
    except StopIteration:
        return None, None


modules = {
    "Crunchyroll": crunchyroll,
    "Zoro": zoro,
    "Twistmoe": twistmoe,
    "Gogoanime": gogoanime,
}

PRIORITY = {"Crunchyroll": 0, "Zoro": 1, "Twistmoe": 2, "Gogoanime": 3}


def fetcher(session, url, check, match):

    mal_sync = session.get(SLUG_SEARCH.format(match.group("slug")))

    if mal_sync.status_code == 404:
        return

    parsed = mal_sync.json()
    alts = session.get(ALTERNATIVES.format(parsed.get("malId"))).json()

    for site, contents in sorted(
        alts.items(), key=lambda x: PRIORITY.get(x[0], float("inf"))
    ):

        if site not in modules:
            continue

        module = modules.get(site)

        for content in contents:
            _, genexp = safe_iter(session, check, module, content.get("url"))
            if genexp is None:
                continue
            else:
                yield _
                yield from genexp
                return
