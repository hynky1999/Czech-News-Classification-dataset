from datasets import concatenate_datasets, load_from_disk
import glob
import os
# %%
import subprocess

for folder in os.listdir('extracted'):
    folder_path = os.path.join('extracted', folder)
    if os.path.isdir(folder_path):
        folder_name = os.path.basename(folder_path)
        print(f"Processing {folder_path}...")

        output_file = f"dataset_{folder_name}"
        subprocess.run(
            ["python", "extraction/postprocess.py", f"{folder_path}/0_file.jsonl", output_file]
        )


dsts = [
    load_from_disk(folder) for folder in glob.glob(os.path.join("./", "dataset_record*"))
]

from datasets import DatasetDict
result = DatasetDict({
    k: concatenate_datasets([dsts[i][k] for i in range(len(dsts))]) for k in dsts[0].keys()
})

result.save_to_disk("dataset")


