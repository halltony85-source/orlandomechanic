"""Submit orlando.mechanicrank.com URLs to IndexNow (Bing, Yandex, Seznam, Naver share it).

    py -3 tools/indexnow.py                            every URL in the live sitemap
    py -3 tools/indexnow.py /blog/some-post/   just these paths

Run it after a deploy that adds pages. build.py writes the key file (INDEXNOW_KEY)
to the site root, and it has to be live before this runs, or every
batch comes back 403. Google does not read IndexNow; it gets the sitemap
through Search Console.
"""
import json
import re
import sys
import urllib.error
import urllib.request

SITE = "https://orlando.mechanicrank.com"
KEY = "7a235db8a65242529056b089b9015136"
BATCH = 10000  # the protocol's per request ceiling


def main(paths):
    if paths:
        urls = [SITE + "/" + p.lstrip("/") for p in paths]
    else:
        xml = urllib.request.urlopen(f"{SITE}/sitemap.xml").read().decode()
        urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        body = json.dumps({"host": "orlando.mechanicrank.com", "key": KEY,
                           "keyLocation": f"{SITE}/{KEY}.txt", "urlList": chunk}).encode()
        req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        print(f"IndexNow HTTP {code} for {len(chunk):,} URLs (200/202 = accepted)")


if __name__ == "__main__":
    main(sys.argv[1:])
