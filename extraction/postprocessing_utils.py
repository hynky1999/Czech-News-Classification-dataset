from datetime import datetime
import json
from typing import List
from dataclasses import dataclass
from enum import IntEnum
from html import unescape
from unicodedata import normalize
import re

import pytz
NONE_STR = "None"


# None ensures compatibility with other classification tasks
class Gender(IntEnum):
    NONE = 0
    MAN = 1
    WOMAN = 2
    MIXED = 3

def published_date_to_date(date: str | None):
    date = datetime.fromisoformat(date)
    if date is None:
        return None

    if date.tzinfo == None:
        date = date.replace(tzinfo=pytz.UTC)

    date_date = date.date()
    return date_date

def create_none_to_x(x):
    def none_to_x_inner(val):
        if val is None:
            return x
        return val

    return none_to_x_inner


def create_filter_by_set(filter_set, lower=False):
    l = filter_set
    if lower:
        l = set(x.lower() for x in filter_set)

    def filter_by_set_inner(val):
        if val is None:
            return None

        is_list = isinstance(val, list)
        val = [val] if not is_list else val

        kept_vals = []
        for v in val:
            v_lower = v.lower() if lower else v
            if v_lower in l:
                kept_vals.append(v)

        if not is_list:
            return kept_vals[0] if len(kept_vals) > 0 else None

        if len(kept_vals) == 0:
            return []
        return kept_vals

    return filter_by_set_inner


def create_translate(translate_dict, lower=False):
    def translate_inner(item):
        if item is None:
            return item
        val = item.lower() if lower else item
        if val in translate_dict:
            return translate_dict[val]

        return item

    return translate_inner


@dataclass
class Article:
    url: str
    server: str
    headline: str
    brief: str | None
    content: str
    category: str | None
    authors: List[str] | None
    authors_gender: List[Gender] | None
    date: str | None
    day: str | None


# AUTHORS
multispace = re.compile(r"\s+")


post_sub = [
    "pro téma",
    "pro právo",
    "pro atm",
    "pro .*dnes(\\.cz)?(\\))?",
    "idnes" "bc(\\.?)",
    "čtk",
    "mgr(\\.?)",
    "ing(\\.?)",
    "phdr(\\.?)",
    "prof(\\.?)",
    "doc(\\.?)",
    "mudr(\\.?)",
]
pre_sub = [
    "připravil(a|i)?",
    "přeložil(a|i)?",
    "zpracoval(a|i)?",
    "zaznamenal(a|i)?",
    "upravil(a|i)?",
    "rozhovor vedli",
    "daňová poradkyně",
    "vizualizace",
    "advokát(ka)?",
    "právní(k|ci)",
    "etoložka",
    "čtenář(ka)?",
    "stránku připravil(a|i)?",
    "kartářka",
    "zahradní architekt(ka)?",
    "kritik",
    "mykoložka",
    "astroložka",
    "politolog",
    "překlad",
    "(odborná)? spolupráce",
    "spolupacoval(a|i)?",
    "redakčně připravil(a|i)?",
    "text(:)?",
    "recenze",
    "kardinál",
    "pro právo",
    "pro téma",
    "pro .*dnes(\\.cz)?",
    "pro novinky(\\.cz)?",
    "bc(\\.?)",
    "mgr(\\.?)",
    "ing(\\.?)",
    "phdr(\\.?)",
    "prof(\\.?)",
    "doc(\\.?)",
    "mudr(\\.?)",
    "lord",
]
pre_sub_re = re.compile(r"^(" + "|".join(pre_sub) + r")\s+", re.IGNORECASE)
post_sub_re = re.compile(r"(" + "|".join(post_sub) + r")$", re.IGNORECASE)


def postprocess_author(author):
    author = preprocess_author(author)
    author = author.lower()
    author = multispace.sub(" ", author)
    author_split = author.split(" ")
    author_split_capitalized = [x.capitalize() for x in author_split]
    author = " ".join(author_split_capitalized)
    author = normalize_text(author)
    return author


def postprocess_authors(authors):
    return [postprocess_author(author) for author in authors] if authors else None



def create_add_gender(gender_mapping):
    def _add_gender(row):
        return list(map(lambda auth: gender_mapping.get(auth, Gender.NONE), row["authors"]))

    return _add_gender




def filter_author(rows):
    authors = rows["authors"]
    if authors == None:
        return None

    new_authors = []
    for author in authors:
        preproc_auth = preprocess_author(author)
        if is_human_author(preproc_auth):
            new_authors.append(author)

    if len(new_authors) == 0:
        return None

    return new_authors


contains_number = re.compile("[0-9]")


def apply_until_not_changed(f, x):
    while True:
        y = f(x)
        if x == y:
            return x
        x = y


def preprocess_author(author):
    # Name like "Jiří Novák | autor" -> "Jiří Novák"
    splitted = author.split("|")[0]
    # Name like "Jiří Novák - autor" -> "Jiří Novák"
    # Spacing is important !!!!!!
    splitted = splitted.split(" - ")[0]
    # Name like "Jiří Novák (autor)" -> "Jiří Novák"
    splitted = splitted.split("(")[0]
    splitted = splitted.split("[")[0]
    striped = splitted.strip()

    # ADD UNTIL NOT CHANGED
    pre_subbed = apply_until_not_changed(lambda x: pre_sub_re.sub("", x), striped)
    post_subbed = apply_until_not_changed(lambda x: post_sub_re.sub("", x), pre_subbed)
    return post_subbed.strip()


def is_capitalized(word):
    return len(word) == 0 or (word[0].isupper() and word[1:].islower())


def is_upper(word):
    return word.isupper()


def is_human_author(author):
    splitted = list(filter(lambda x: len(x) > 0, author.split(" ")))
    non_whitespace_author = author.replace(" ", "")

    if len(splitted) > 4 or len(splitted) < 2:
        return False

    # At least 2 letters in every word
    if not all([len(word) > 2 for word in splitted]):
        return False

    if not non_whitespace_author.isalnum():
        return False

    if contains_number.search(author):
        return False

    return True


def cap_with_dot(headline):
    # Capitalize and adds dot
    if headline == None:
        return None

    headline = headline.strip()
    if len(headline) >= 2 and headline[-1] == "." and headline[-2] != ".":
        headline = headline[:-1]

    if len(headline) > 1 and headline[0].islower():
        headline = headline[0].upper() + headline[1:]

    return headline


DAYS = [NONE_STR ,"MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
# DATE
def postprocess_date(date):
    date = published_date_to_date(date)
    return date

def add_day(item):
    date = item["date"]
    if date is None:
        return 0

    day = date.weekday() + 1
    return day

re_multispace = re.compile(r"\s+")


def normalize_text(text):
    if text == None:
        return None

    text = text.strip()
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")
    text = re_multispace.sub(" ", text)
    text = unescape(text)
    text = normalize("NFKC", text)
    return text


# HEADLINE
def postprocess_headline(headline):
    return normalize_text(cap_with_dot(headline))


# BRIEF
def postprocess_brief(brief):
    return normalize_text(cap_with_dot(brief))


def postprocess_content(content):
    return normalize_text(content)


def postprocess_keywords(keywords):
    if keywords is None:
        return None

    return [cap_with_dot(normalize_text(keyword.lower())) for keyword in keywords]

def postprocess_category(category):
    if category != None:
        category = category.lower()

    category = cap_with_dot(category)
    return category


def add_server(server):
    def add_server_inner(js):
        js["server"] = server
        return js

    return add_server_inner


def add_cum_gender(dst):
    genders = dst["authors_gender"]
    if len(genders) == 0:
        return Gender.NONE

    g_type = Gender.MIXED
    for g in Gender:
        if all(gender == g for gender in genders):
            g_type = g
            break
    return g_type


def as_Article(js):
    return js


class JSONArticleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Gender):
            return obj.name

        if isinstance(obj, datetime.date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
