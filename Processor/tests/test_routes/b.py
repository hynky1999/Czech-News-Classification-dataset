from Extractor.extractor import BaseExtractor
from utils import PipeMetadata


NAME = "BBB"


class Extractor(BaseExtractor):
    def extract_soup(self, response: str, metadata: PipeMetadata):
        return None

    def filter(self, response: str, metadata: PipeMetadata) -> bool:
        return True