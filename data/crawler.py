import json
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re
from collections import Counter

def get_html(url):
    req = requests.get(url)
    html = req.text
    return html

def crawl_list(url, pattern):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('main')

url = "https://nips.cc/Conferences/2020/AcceptedPapersInitial"
html = get_html(url)


# Suppose I can always use three step to find target elements
# 1. Find the first element contains paper
# 2. Find the container contains all papers, For ICLR which uses different containers for oral/poster/reject, just find all oral papers, or all poster papers in one step.
# 3. List those elements

def find_target_elements(html, pattern):
    eles = pattern.split("/")
    soup = BeautifulSoup(html, 'lxml')
    lists = soup.select(eles[0])
    for l in lists:
        print(l.text)
        if l.text == 'Continuous Surface Embeddings':
            break

    if eles[1] == '..':
        container = l
        for i in range(len(eles[0].split(">"))):
            container = container.parent
    if '@' in eles[2]:
        selector, index = eles[2].split("@")
    container_lists = container.select(selector)
    if ':' not in index:
        nodes = container_lists[int(index) - 1]
    else:
        start, end = index.split(":")
        start = (int(start) - 1) if start else 0
        end = (int(end) - 1) if end else len(container_lists)
        nodes = container_lists[start:end]
    return nodes


nodes = find_target_elements(html, "p>b/../p@3:")


pass_and = ['science and technology', 'technology and design', 'aeronautics and astronautics', 'mathematics and computer', 
            'posts and telecommunications', 'finance and economics', 'engineering and management', 'processing and speech', 'business and economics',
            'analysis and navigation', 'electronics and telecommunications', 'economics and statistic'
           ]


def author_parser(text):
    institute_list = []
    left = 0
    institute = ""
    for c in text:
        if c == '(':
            left += 1
            if left == 1:
                institute = institute.strip()
                institute_list.append(institute)
                institute = ""
        if c == ')':
            left -= 1
            continue
        if left > 0 or c == '·':
            continue
        institute += c
    return institute_list




def institute_parser(text):
    institute_list = []
    left = 0
    institute = [""]
    for i, c in enumerate(text):
        if c == '(':
            left += 1
            if left == 1:
                continue
        elif c == ')':
            left -= 1
            if left > 0:
                continue
            if left == 0:
                institute[-1] = institute[-1].replace('  ', ' ').replace(', China', '').strip()
                institute_list.append(institute)
                institute = [""]
        if left == 0 or left > 1 or c == '"':
            continue
        if c in ['&', '/']:
            if i - 2 > 0 and c == '&' and text[i-1:i+2] == 'A&M':
                institute[-1] += c
                continue
            institute[-1] = institute[-1].replace('  ', ' ').replace(', China', '').strip()
            institute.append('')
            continue
        institute[-1] += c
    
    for j, e in enumerate(institute_list):
        for i, c in enumerate(e):
            if len(c) < 2:
                institute_list[j][i] = ''
            if ' and ' in c:
                try:
                    if c.find('Petuum') !=-1 and 'London' in c.split():
                        #c.replace('Petuum')
                        # print('=='*20)
                        # print(c)
                        # print('here'*20)
                        c = 'Petuum and Imperial College London'

                    phrase = re.findall('(\w+ and +\w+)', c)[0].lower()
                except:
                    print("=="*5, c, "=="*20)
                    if 'Brains, Minds, and Machines' not in c:
                        raise IndexError
                    else:
                        continue
                if phrase in pass_and:
                    continue
                else:
                    index = c.find(' and ')
                    new_one = c[index+5:]
                    institute_list[j][i] = c[:index]
                    institute_list[j].append(new_one)
    return institute_list



# e = 'Ziyu Jiang (Texas A&M University) · Yue Wang (Rice University) · Xiaohan Chen (Texas A&M University) · Pengfei Xu (Rice University) · Yang Zhao (Rice University) · Yingyan Lin (Rice University) · Zhangyang Wang (TAMU)'
# # aut = author_parser(e)
# inst = institute_parser(e)
# print(inst)
# e='Maithra Raghu (Cornell University and Google Brain) · Chiyuan Zhang (Google Brain) · Jon Kleinberg (Cornell University) · Samy Bengio (Google Research, Brain Team)'
# inst = institute_parser(e)
# print(inst)

# e='zengfeng Huang (Fudan University) · Ziyue Huang (HKUST) · Yilei WANG (The Hong Kong University of Science and Technology) · Ke Yi (" Hong Kong University of Science and Technology, Hong Kong")'
# inst = institute_parser(e)
# print(inst)

# e='Kevin Ellis (MIT) · Maxwell Nye (MIT) · Yewen Pu (MIT) · Felix Sosa (Harvard and Center for Brains, Minds, and Machines) · Josh Tenenbaum (MIT) · Armando Solar-Lezama (MIT)'
# inst = institute_parser(e)
# print(inst)


def extract_item(element, rules):
    paper_item = {}
    extra_item = []
    for key in rules:
        if isinstance(rules[key], str):
            paper_item[key] = element.select(rules[key])[0].text
        elif isinstance(rules[key], list):
            text = element.select(rules[key][0])[0].text

            # Let's only consider author and/or institute
            if key == 'authors':
                if isinstance(rules[key][1]['author'], str):
                    author_list = re.findall(rules[key][1]['author'], text)
                else:
                    author_list = rules[key][1]['author'](text)
                if isinstance(rules[key][1]['institute'], str):
                    institute_list = re.findall(rules[key][1]['institute'], text)
                else:
                    print(text)
                    institute_list = rules[key][1]['institute'](text)
                item = tuple(zip(author_list, institute_list))
                assert len(author_list) == len(institute_list)
            else:
                print("not authors")
                raise NotImplementedError
            paper_item[key] = item
    return paper_item

# # (Facebook AI research (FAIR)) makes regular expression fail
rules = {'title': 'p>b', 'authors': ['i', {'author': ' ?([^(·]+) \([^(]+\)', 'institute': '[^(·]+ \(([^(]+)\)'}]}
rules = {'title': 'p>b', 'authors': ['i', {'author': author_parser, 'institute': institute_parser}]}

paper_set = {}
for element in nodes:
    item = extract_item(element, rules)
    title = item.pop('title')
    paper_set[title] = item


def check_2_and(paper_set):
    for e in paper_set:
        for a in paper_set[e]['authors']:
            a = list(a)
            for i, c in enumerate(a[1]):
                if 0 < len(c) < 2:
                    print(c, a)
                if ' and ' in c:
                    print(c)



import re
phrases = []
for e in paper_set:
    for a in paper_set[e]['authors']:
        for c in a[1]:
            if ',' in c:
                phrases.append(c)



print(Counter(phrases))


def main(url):

    html = get_html(url)

    nodes = find_target_elements(html, "p>b/../p@3:")
    rules = {'title': 'p>b', 'authors': ['i', {'author': author_parser, 'institute': institute_parser}]}

    paper_set = {}
    for element in nodes:
        item = extract_item(element, rules)
        title = item.pop('title')
        paper_set[title] = item
    return paper_set

url = "https://nips.cc/Conferences/2020/AcceptedPapersInitial"
url = "https://papers.nips.cc/book/advances-in-neural-information-processing-systems-32-2019"
paper_set = main(url)
print(len(paper_set))

with open('data/neurips2019.json', 'w') as fp:
    json.dump(paper_set, fp, indent=4)