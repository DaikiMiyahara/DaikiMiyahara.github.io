import requests
import bibtexparser
from bs4 import BeautifulSoup
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

print("Type the title")
title = input()


# springer内で目的を検索
url = 'https://link.springer.com/search?query=' + title
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')


# 目的のurlとhtmlをget
url = 'https://link.springer.com/' + soup.find('h2').a['href']
r = requests.get(url)
url = url.split("chapter/")


# 目的のbibtexのurlとhtmlをget
url_bib = 'https://citation-needed.springer.com/v2/references/' + url[1]
payload = {"format": "bibtex", "flavour": "citation"}
r_bib = requests.get(url_bib, params=payload)

# 目的のhtmlとbibtexのhtmlパース用のオブジェクト作成
soup = BeautifulSoup(r.text, 'lxml')
soup_bib = BeautifulSoup(r_bib.text, 'lxml')

# cite this paper as 以降のtextを取得
cite = soup.select_one("#citethis-text").text

# cite からvolume を取得
cite_spl = cite.rsplit('. Springer')
cite_spl = cite_spl[0]
cite_spl = cite_spl.rsplit('vol ')
volume = cite_spl[1]

# bibファイルのtextを取得
bib = soup_bib.find('p').text

# bib からabst 情報を消す
bib_abst_index = bib.rfind('abstract=')
bib_isbn_index = bib.rfind('isbn=')
abst = ''
for x in range(bib_isbn_index - bib_abst_index):
	abst = abst + bib[x+bib_abst_index]
bib = bib.rsplit(abst)
bib = bib[0] + bib[1]

# bib にvolume とsereise を入れる
bib = bib.rstrip('}\n')
bib = bib + ',\n' + 'series="Lecture Notes in Computer Science",\n' + 'volume="' + volume +'"\n}\n'
print(bib)

# bib のpublisher をSpringer に直す
bib_publ_index = bib.rfind('publisher=')
bib_addr_index = bib.rfind('address=')
publ = ''
for x in range(bib_addr_index - bib_publ_index):
	publ = publ + bib[x+bib_publ_index]
bib = bib.replace(publ, 'publisher="Springer",\n', 1)

# bib にID を入れる
print("type the desired ID of the bibtex")
bib_id = input()
bib_id_lindex = bib.find('{')
bib_id_rindex = bib.find(',\n')
temp = ''
for x in range(bib_id_rindex - bib_id_lindex - 1):
	temp = temp + bib[x + 1 + bib_id_lindex]
bib = bib.replace(temp, bib_id, 1)
print('\n')
print(bib)

# 加えるかの確認をしてから，bibtex.bib にbib を加える
print("add the above bibtex, right? type y if O.K.")
flag = input()
if flag == 'y':
	with open('bibtex.bib') as bibtex_file:
		bibtex_str = bibtex_file.read()
	bibtex_database = bibtexparser.loads(bibtex_str+bib)
	with open('bibtex.bib', 'w') as bibtex_file:
		bibtexparser.dump(bibtex_database, bibtex_file)
