# %%
import json
from datetime import datetime
from pathlib import Path
import sys

from tqdm import tqdm

NUM_PROCESS = 4
from datasets import Dataset
from datasets import Features, Value
from urllib.parse import urlparse
from datasets import Sequence
from postprocessing_utils import (
    postprocess_authors,
    add_day,
    create_translate,
    create_filter_by_set,
    postprocess_brief,
    postprocess_category,
    postprocess_headline,
    postprocess_date,
    postprocess_content,
    add_cum_gender,
    create_add_gender,
    postprocess_keywords,
    create_none_to_x,
)
from authors_utils import auts 
from categories_utils import translate_cat_cz_en, translate_cat
from functools import reduce
from datasets import ClassLabel, Sequence
from datasets import DatasetDict


def get_server(url):
    parsed = urlparse(url).netloc.split(".")
    server = parsed[-1]
    if server == "cz":
        server = parsed[-2]

    if server == "cz:443":
        server = "aktualne"

    return server


def crawl(file_path, output_path):
    records = []
    print("Loading records from file")
    with open(file_path) as f:
        for line in tqdm(f):
            records.append(json.loads(line))

    print("Generating dataset")
    dataset = Dataset.from_list(
        records,
        features=Features(
            {
            "url": Value("string"),
            "author": Sequence(Value("string")),
            "headline": Value("string"),
            "brief": Value("string"),
            "publication_date": Value("string"),
            "keywords": Sequence(Value("string")),
            "category": Value("string"),
            "content": Value("large_string"),  
            "comments_num": Value("int32"),
            "domain_record": {
                "digest": Value("string"),
                "encoding": Value("string"),
                "filename": Value("string"),
                "length": Value("int32"),
                "offset": Value("int32"),
                "timestamp": Value("string"),
                "url": Value("string"),
            },
            "additional_info": {
                "sets": Sequence(Value("string")),
            }
            }
        )
    )
    # We will postprocess string values later and cast it manually
    dataset = dataset.map(lambda batch: {"server": [get_server(url) for url in batch["url"]]}, num_proc=NUM_PROCESS, batched=True)


    # %%


    postprocessing = {
        "category": [create_translate(translate_cat, lower=True), postprocess_category, create_filter_by_set(set(translate_cat_cz_en.keys()), lower=True),
        create_translate(translate_cat_cz_en)],
        "authors": [postprocess_authors, create_filter_by_set(set(auts.keys()), lower=True), create_none_to_x([])],
        "brief": [postprocess_brief],
        "headline": [postprocess_headline],
        "content": [postprocess_content],
        "publication_date": [postprocess_date],
        "keywords": [postprocess_keywords, create_none_to_x([])]
    }

    # %%
    def to_date(date_str):
        if date_str is None:
            return None
        return datetime.fromisoformat(date_str).date()

    print("Postprocessing")
    dataset = dataset.map(lambda batch: {"category_unclean": batch["category"]}, batched=True, num_proc=NUM_PROCESS)


    dataset = dataset.rename_column("author", "authors")

    for col, funcs in postprocessing.items():
        dataset = dataset.map(lambda batch: {col: reduce(lambda arts, f:[ f(art) for art in arts], funcs, batch[col])}, batched=True, num_proc=NUM_PROCESS)



    # Convert to date
    dataset = dataset.map(
        lambda batch: { "date": [to_date(dtm) for dtm in batch["publication_date"]] }
        , batched=True, batch_size=None, num_proc=NUM_PROCESS, remove_columns=["publication_date"]
    )
    print("Adding augmentations")

    # %%
    augmentations = {
        "authors_gender": create_add_gender(auts),
        "authors_cum_gender": add_cum_gender,
        "day_of_week": add_day,
    }




    for col, func in augmentations.items():
        dataset = dataset.map(lambda batch: {col: func(batch)}, batched=False, num_proc=NUM_PROCESS)


    print("Casting columns to categorical")
    # %%
    NONE_LABEL = "None"

    def NoneToNoneLabel(dst, column):
        return dst.map(lambda batch: {column: [NONE_LABEL if x is None else x for x in batch[column]]}, batched=True, num_proc=NUM_PROCESS)


    # %%
    features = {
        "category": ClassLabel(names=[NONE_LABEL] + list(translate_cat_cz_en.values())),
        "authors_cum_gender": ClassLabel(names=[NONE_LABEL, "Man", "Woman", "Mixed"]),
        "authors_gender": Sequence(ClassLabel(names=[NONE_LABEL ,"Man", "Woman"])),
        "day_of_week": ClassLabel(names=[NONE_LABEL ,"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]),
        "server": ClassLabel(names=[NONE_LABEL, "idnes", "denik", "aktualne", "irozhlas", "seznamzpravy", "novinky"]),
    }




    # %%
    cast_columns = ["category", "server", "day_of_week"]
    for col in cast_columns:
        dataset = NoneToNoneLabel(dataset, col)
        dataset = dataset.cast_column(col, features[col])

    cast_columns = ["authors_gender", "authors_cum_gender", ]
    for col in cast_columns:
        dataset = dataset.cast_column(col, features[col])


    print("Splitting into sets")
    # %%
    splits = {
        "test_human": [],
        "train": [],
        "test": [],
        "validation": [],
        "train_small": [],
        "test_small": [],
    }

    for i,row in enumerate(dataset):
        for split in row["additional_info"]["sets"]:
            splits[split].append(i)

    splits = {k: dataset.select(v) for k,v in splits.items()}
    final = DatasetDict(splits)

    # %%
    final = final.remove_columns(["additional_info", "domain_record"])

    # %%
    final["train"].features

    # %%
    final["train"].features

    # %%
    final.save_to_disk(output_path)





if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 crawl.py <path_to_file> <path_to_output>")
        exit(1)

    sys.path.append(Path(__file__).parent)
    crawl(Path(sys.argv[1]), Path(sys.argv[2]))