import regex

EMBED_URL_REGEX = regex.compile(r"(.+?/)(?:embed|e)/([^?/#&])")


def extract(session, url, **opts):
    host, slug = EMBED_URL_REGEX.search(url).group(1, 2)

    vidstream_info = session.get(
        "{}info/{}".format(host, slug), headers={"referer": host}
    )
    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json().get("media", {}).get("sources", [])
        if not content.get("file", "").endswith("m3u8")
    ]
