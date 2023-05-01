import logging
from pathlib import Path
from datetime import datetime
import json
import unittest
from shutil import rmtree
from cmoncrawl.integrations.commands import extract_from_files, ExtractMode
from cmoncrawl.common.types import ExtractConfig

from cmoncrawl.common.loggers import metadata_logger, all_purpose_logger
all_purpose_logger.setLevel(logging.DEBUG)
metadata_logger.setLevel(logging.DEBUG)


TRUTH_JSONS = "truth"
TEST_ARTICLES = "test_articles"
FILTER_ARTICLES = "filter_articles"


def parse_extracted_json(extracted_path: Path):
    with open(extracted_path, "r") as f:
        extracted = json.load(f)
    if extracted["publication_date"] is not None:
        extracted["publication_date"] = datetime.fromisoformat(
            extracted["publication_date"]
        )
    return extracted

async def pipeline_wrapper(config: ExtractConfig, files_path: Path, output_path: Path, name: str):
    files = [path for path in files_path.glob("*")]

    output_path = output_path / name
    await extract_from_files(
        config=config,
        files=files,
        mode=ExtractMode.HTML,
        date=None,
        url=None,
        output_path=output_path,
        max_crawls_per_file=1,
        max_directory_size=10000,
        debug=True,
    )

    data = []
    for file in (output_path / "directory_0").glob("*"):
        with open(file, "r") as f:
            data.append(json.load(f))
    data = {d["domain_record"]["filename"]: d for d in data}
    for d in data:
        del(data[d]["domain_record"])

    for k,v in data.items():
        if v["publication_date"] is not None:
            data[k]["publication_date"] = datetime.fromisoformat(v["publication_date"])
    return data


class ExtractSameTest(unittest.IsolatedAsyncioTestCase):



    def setUp(self) -> None:
        config_path = Path("config.json")
        with open(config_path, "r") as f:
            cfg = json.load(f)
            self.config = ExtractConfig.schema().load(cfg)
        self.name = ""
        self.base_path = Path(__file__).parent
        self.sites_path = self.base_path / "sites"
        self.output_path = self.base_path / "output"

    def tearDown(self) -> None:
        pth = self.output_path / self.name
        if pth.exists():
            rmtree(pth, ignore_errors=True)
        

    async def test_extract_articles(self):
        if type(self) == ExtractSameTest:
            return

        data = await pipeline_wrapper(self.config, self.sites_path / Path(self.name) / TEST_ARTICLES, self.output_path, self.name)
        for truth_json in (self.sites_path / self.name / TRUTH_JSONS).iterdir():
            extracted_truth = parse_extracted_json(truth_json)
            self.assertIn(truth_json.stem + ".html", data.keys())
            extracted = data[truth_json.stem + ".html"]
            self.maxDiff = None
            self.assertDictEqual(extracted, extracted_truth)

    async def test_filter_articles(self):
        if type(self) == ExtractSameTest:
            return

        data = await pipeline_wrapper(self.config, self.sites_path / Path(self.name) / FILTER_ARTICLES, self.output_path, self.name)
        self.assertListEqual(list(data.keys()), [])


class IrozhlasTests(ExtractSameTest):
    def setUp(self) -> None:
        super().setUp()
        self.name = "rozhlasCZ"


class SeznamZpravyCZ(ExtractSameTest):
    def setUp(self) -> None:
        super().setUp()
        self.name = "seznamzpravyCZ"


class NovinkyCZTests(ExtractSameTest):
    def setUp(self) -> None:
        super().setUp()
        self.name = "novinkyCZ"


class AktualneCZTests(ExtractSameTest):
    def setUp(self) -> None:
        super().setUp()
        self.name = "aktualneCZ"


class IdnesCZ(ExtractSameTest):
    def setUp(self) -> None:
        super().setUp()
        self.name = "idnesCZ"


class DenikCZ(ExtractSameTest):
    def setUp(self) -> None:
        super().setUp()
        self.name = "denikCZ"


class IhnedCZ(ExtractSameTest):
    def setUp(self) -> None:
        super().setUp()
        self.name = "ihnedCZ"
