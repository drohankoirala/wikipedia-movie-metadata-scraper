import re
import time
from colorama import Fore
import requests
from lxml.html import fromstring

prev = time.time()


class Scraper:
    def __init__(self):
        self._selector = None
        self.meta = {}
        self.character = {}
        self._id = ""
        self._name = ""
        self._table_path = '//*[@id="mw-content-text"]/div[1]/table[1]/tbody/tr'

    def _extract_imdbId(self):
        trf = self._selector.xpath('//a[starts-with(@href, "https://www.imdb.com/title/")]')
        id_ = None
        if trf:
            trf = trf[-1]
            id_ = [_ for _ in trf.xpath(".//@href")[0].split("/") if _][-1]
        if not id_:
            return False
        self._id = id_
        img = ''.join(self._selector.xpath(self._table_path + "//td//img//@src"))
        if not self.meta.get(id_):
            self.meta[id_] = {}
        self.meta[id_]['wiki_url'] = self._selector.xpath('//link[@rel="canonical"]/@href')[0]
        if img:
            self.meta[id_]['poster'] = 'https:' + img
        return id_

    @staticmethod
    def _return_entire_text_of_node(node):
        if len(node) == 1 and node:
            return node[0].xpath(".//text()")
        text = ""
        for lkn in node:
            text += lkn.xpath(".//text()")
        return text

    def _extract_genre(self):
        kjn = ''.join(
            [''.join(_.xpath(".//text()")) for _ in self._selector.xpath('//*[@id="mw-content-text"]/div[1]/p')[:5]])
        kjn = re.search(r"language(.*?)film", kjn, re.IGNORECASE)
        if kjn:
            knv = []
            for jgv in kjn.group(1).split(" "):
                if jgv:
                    knv.append(jgv)
            self.meta[self._id]['genre'] = knv

    def _extract_table_data(self):
        for kjn in self._selector.xpath(self._table_path):
            th = [' '.join(_.xpath(".//text()")) for _ in kjn.xpath(".//th")]
            td = ', '.join([_ for _ in kjn.xpath(".//td//text()") if _]).replace("\xa0", ' ')
            if not th or not td:
                continue
            th = th[0]
            og = td
            if th == "Release date" or th == "Release dates":
                td_ = re.search(r"\b(\d{1,2} [A-Z][a-z]+ \d{4})|(\d{4}-\d{2}-\d{2})|(20\d{2})|(19\d{2})\b", og)
                if td_:
                    td = td_.group()
            elif th == "Running time":
                td_ = re.search(r"\b(\d{1,3} [a-z]+)\b", og)
                if td_:
                    td = td_.group()
            elif th == "Budget" or th == "Box office":
                td_ = re.search(r"(\d+.\d+)|(\d+)", og)
                if td_:
                    td = "₹" + td_.group()
                td_ = re.search(r"([clmb][a-z]+)", og, re.IGNORECASE)
                if td_:
                    td = td + " " + td_.group()
            elif th.lower() in ['directed by', 'produced by', 'production companies', 'story by', 'written by',
                                'cinematography', 'edited by', 'production company', 'budget', 'box office', 'country',
                                'languages', 'language']:
                td = re.findall(r"\b[A-Z][a-z0-9]*[.\-]?(?: [A-Z]\.){0,2}(?: ?[A-Z][a-z0-9]*){0,3}\b", og)

            else:
                continue
            self.meta[self._id][th] = td

    # def _extract_cast_data(self):
    #     noted = False
    #     if self.meta.get(self._id, {}).get('casts'):
    #         del self.meta[self._id]['casts']
    #     for kjn in self._selector.xpath('//*[@id="mw-content-text"]/div[1]')[0]:
    #         if "cast [ edit ]" in ' '.join([_ for _ in kjn.xpath(".//text()")]).lower():
    #             noted = True
    #         elif (kjn.tag == "div" or kjn.tag == "ul") and noted:
    #             for _ in kjn.xpath(".//li"):
    #                 all_text = ''.join(_.xpath(".//text()"))
    #                 all_text = all_text.replace("\xa0", '')
    #                 all_text = all_text.split('\n')[0].split(', ')[0].split(' as ')
    #                 for ind, lkn in enumerate(all_text.copy()):
    #                     k = re.search(r"[A-Z]*[a-z]*[\-.']?(?:\s[A-Z]*[a-z]*[\-.']){0,2}", lkn)
    #                     if k:
    #                         k = k.group()
    #                     all_text[ind] = k or lkn
    #
    #                 if len(all_text) < 2:
    #                     all_text.append("--undef--")
    #                 chr_name = all_text[0]
    #                 chr_role = all_text[1]
    #                 cast_wiki_url = _.xpath(".//@href")
    #                 if cast_wiki_url:
    #                     cast_wiki_url = cast_wiki_url[0]
    #                 cast_id = cast_wiki_url.replace("/wiki/", '') if "/wiki/" in cast_wiki_url else chr_name
    #                 self.character[cast_id] = self.character.get(chr_name, {
    #                     "wiki_url": ("https://en.wikipedia.org" + cast_wiki_url) if cast_wiki_url else "",
    #                     "name": chr_name, "movies": {}
    #                 })
    #                 self.character[cast_id]["movies"][self._id] = {
    #                     "role": chr_role,
    #                     "title": self._name
    #                 }
    #                 self.meta[self._id]['casts'] = self.meta[self._id].get('casts', {})
    #                 self.meta[self._id]['casts'][cast_id] = {
    #                     "name": chr_name,
    #                     "role": chr_role
    #                 }
    #             break

    def _extract_cast_data(self):
        noted = False
        if self.meta.get(self._id, {}).get('casts'):
            del self.meta[self._id]['casts']
        for kjn in self._selector.xpath('//*[@id="mw-content-text"]/div[1]')[0]:
            if "cast [ edit ]" in ' '.join([_ for _ in kjn.xpath(".//text()")]).lower():
                noted = True
            elif (kjn.tag == "div" or kjn.tag == "ul") and noted:
                for _ in kjn.xpath(".//li"):
                    all_text = _.xpath(".//text()")
                    comb = ''.join(all_text)
                    final_text = comb.split('\n')[0].split(', ')[0].split(' as ')
                    if len(final_text) < 2:
                        final_text.append("--undef--")
                    chr_name = final_text[0]
                    chr_role = final_text[1]
                    cast_wiki_url = _.xpath(".//@href")
                    if cast_wiki_url:
                        cast_wiki_url = cast_wiki_url[0]
                    cast_id = cast_wiki_url.replace("/wiki/", '') if "/wiki/" in cast_wiki_url else chr_name
                    self.character[cast_id] = self.character.get(chr_name, {
                        "wiki_url": ("https://en.wikipedia.org" + cast_wiki_url) if cast_wiki_url else "",
                        "name": chr_name, "movies": {}
                    })
                    self.character[cast_id]["movies"][self._id] = {
                        "role": chr_role,
                        "title": self._name
                    }
                    self.meta[self._id]['casts'] = self.meta[self._id].get('casts', {})
                    self.meta[self._id]['casts'][cast_id] = {
                        "name": chr_name,
                        "role": chr_role
                    }
                break

    def _get_table(self):
        c = 0
        for ind, lkm in enumerate(self._selector.xpath('//*[@id="mw-content-text"]/div[1]/table/tbody')):
            for nbv in lkm:
                th = ''.join(nbv.xpath(".//th/text()"))
                if th.lower() in ['directed by', 'produced by', 'production companies', 'story by', 'written by',
                                  'cinematography', 'edited by', 'production company', 'budget', 'box office',
                                  'country',
                                  'languages', 'language']:
                    c += 1
                    if c < 3:
                        continue
                    self._table_path = f'//*[@id="mw-content-text"]/div[1]/table[{ind + 1}]/tbody/tr'
                    self._name = ''.join(self._selector.xpath(f"""{self._table_path}[1]/th//text()"""))
                    self.meta[self._id]['name'] = self._name
                    return

    def decode_page(self, html):
        self._selector = fromstring(html)
        try:
            self._extract_imdbId()
            self._get_table()
            self._extract_genre()
            self._extract_table_data()
            self._extract_cast_data()
        except Exception as e:
            print(Fore.RED + f"| Errr - {str(time.time() - prev)[:5]} sec [{e}]" + Fore.RESET)
            time.sleep(1.5)
        print(Fore.RED + f"| Done - {str(time.time() - prev)[:5]} sec [Curled]" + Fore.RESET)

    @staticmethod
    def decode_url(url_, **argv):
        return requests.get(url_, **argv).content


urls = []  # list of urls to fetch metadata
if __name__ == "__main__":
    scraper = Scraper()
    for url in urls:
        scraper.decode_page(scraper.decode_url(url))
    print(scraper.meta)
    print(scraper.character)
