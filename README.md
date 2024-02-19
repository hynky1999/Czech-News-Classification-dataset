# Short description
This repository contains download instructions for downloading
CZEch NEws Classification dataset (CZE-NEC).

Among others this repository also showcases how to use [cmoncrawl](https://github.com/hynky1999/CmonCrawl) with Artemis queue as middleware for distributed extraction.

# Download CZE-NEC dataset

First make sure that you also downloaded lfs files. To do that run git lfs pull.

## Install dependencies
```bash pip install -r requirements.txt```

## Download dataset
```bash cmon extract --n_proc=4 Processor/config.json extracted records/*.jsonl record --max_retry=500```
This will download records from cmoncrawl and save them to records directory.
Adjust n_proc to number of processes you want to use, max_retry defines number of retries for failed downloads.
S3 buckets are currently under heavy load, thus you will get many failed attempts, don't be scared by that, it will
try to retry 500 times, it will just take some time (For me it took 30 hours to download).

## Concatenate records
```bash cat extracted/*/*/*.jsonl > records.jsonl```
This will take files and merge them into single file (You can use cat or anything else you want).
Due to memory issues, I had to split the records into multiple files.
```cat records.jsonl | split -n l/10 records.jsonl```

## Postprocess records (High-mem usage)
```python extraction/postprocess.py records.jsonl dataset --num_proc=4```

This will take records and postprocess them into dataset directory.

## Postprocess records (Low-mem usage)
```python ./low_mem-usage_postprocess.py```

## Loading dataset
To load dataset just run ```datasets.load_from_disk('dataset')```, since dataset is saved using HuggingFace datasets library.

## [Important] Memory usage
You migh run into some trouble with memory. Since postprocessing scripts loads all the samples into memory, you might run out of memory. To fix this,
you can concatenate records into multiple files and postprocess them separately. This will result in multiple datasets, which you can then merge together
using ```datasets.concatenate_datasets```. Second option is to change --num_proc to lower number, which will result in lower memory usage, but also slower
postprocessing. I managed to run with 4 on 100GB RAM (yes you read that right, 100GB RAM).

## [Important] datasets.Dataset generator
Note that the generation has no progress bar, so it might look like it is stuck. I tried adding tqdm, but it doesn't work.

## Contact
If you have any questions, feel free to contact me at kydlicek.hynek@gmail.com

## How as the dataset gather ?
Since the data was already preprocess and correct indexes have been found, there is no need for you to run it in distributed setting. You will download about 1.6M files,
however when we collected the batch for processsing we downloaded around 70M+ Files, in which many were duplicated yielding of around 6M for further filtering.
We thus needed a distributed collections. If you want to do it you can :). If on slurm run grid_run.sh, which will spawn queue, processors and aggregaors, based on definitions in grid_run.sh.
Similary you can use docker-swarm since we prepared a docker-compose too
