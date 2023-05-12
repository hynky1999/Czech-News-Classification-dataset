# Short description
This repository contains download instructions for downloading
CZEch NEws Classification dataset (CZE-NEC).

Among others this repository also showcases how to use [cmoncrawl](https://github.com/hynky1999/CmonCrawl) with Artemis queue as middleware for distributed extraction.


# Download CZE-NEC dataset

## Install dependencies
```bash pip install -r requirements.txt```

## Download dataset
```bash cmon extract --n_proc=4 Processor/config.json extracted records/*.jsonl record --max_retry=500```
This will download records from cmoncrawl and save them to records directory.
Adjust n_proc to number of processes you want to use, max_retry defines number of retries for failed downloads.
You should see processed 1627267 urls in the end.

## Concatenate records
```bash cat extracted/*/*.jsonl records.jsonl```
This will take files and merge them into single file (You can use cat or anything else you want).
Due to memory issues, I had to split the records into multiple files.
```cat records.jsonl | split -n l/10 records.jsonl```

## Postprocess records
```python extraction/postprocess.py records.jsonl dataset```

This will take records and postprocess them into dataset directory.

## Loading dataset
To load dataset just run ```datasets.load_from_disk('dataset')```, since dataset is saved using HuggingFace datasets library.

## [Important] Memory usage
You migh run into some trouble with memory. Since postprocessing scripts loads all the samples into memory, you might run out of memory. To fix this,
you can concatenate records into multiple files and postprocess them separately. This will result in multiple datasets, which you can then merge together
using ```datasets.concatenate_datasets```.

## [Important] datasets.Dataset generator
Note that the generation has no progress bar, so it might look like it is stuck. I tried adding tqdm, but it doesn't work.

## [Important] Dataset size
The dataset is currently missing 143 samples. That's due to the fact that during the extraction, I didn't save the domain records and I had to 
find the domain records afterwards. I used AWS athena for search in index, but it doesn't contain the first 3 crawls. 
Currently the index is completely unusable due to traffice, so I can't find the missing records. I will update the dataset as soon as I find the missing records.

## Contact
If you have any questions, feel free to contact me at kydlicek.hynek@gmail.com