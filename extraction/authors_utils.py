from pathlib import Path
from postprocessing_utils import Gender
auts = {}
with open(Path(__file__).parent / "authors.txt") as f:
    for line in f:
        author, gender = line.split(",")
        gender = Gender.MAN if gender.strip() == "male" else Gender.WOMAN
        auts[author] = gender
