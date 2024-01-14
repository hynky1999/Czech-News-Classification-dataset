from typing import Any, Callable, Dict, List
from bs4 import BeautifulSoup
from cmoncrawl.common.types import PipeMetadata
from cmoncrawl.processor.pipeline.extractor import BaseExtractor
from cmoncrawl.processor.extraction.utils import check_required
from cmoncrawl.common.loggers import metadata_logger
from cmoncrawl.processor.extraction.filters import (
    must_exist_filter,
    must_not_exist_filter,
)
from cmoncrawl.processor.extraction.utils import (
    extract_transform,
    combine_dicts 
)

class ArticleExtractor(BaseExtractor):
    def __init__(
        self,
        header_css_dict: Dict[str, str] = {},
        header_extract_dict: Dict[
            str, List[Callable[[Any], Any]] | Callable[[Any], Any]
        ] = {},
        article_css_dict: Dict[str, str] = {},
        article_extract_dict: Dict[
            str, List[Callable[[Any], Any]] | Callable[[Any], Any]
        ] = {},
        article_css_selector: str = "body",
        filter_must_exist: List[str] = [],
        filter_must_not_exist: List[str] = [],
        filter_allowed_domain_prefixes: List[str] | None = None,
        encoding: str | None = None
    ):
        super().__init__(encoding=encoding)
        self.header_css_dict = header_css_dict
        self.header_extract_dict = header_extract_dict
        self.article_css_dict = article_css_dict
        self.article_extract_dict = article_extract_dict
        self.article_css_selector = article_css_selector
        self.filter_must_exist = filter_must_exist
        self.filter_must_not_exist = filter_must_not_exist
        self.filter_allowed_domain_prefixes = filter_allowed_domain_prefixes
        self.required_check_fc = check_required(
            {
            "content": True,
            "headline": True,
            "author": True,
            "brief": False,
            "publication_date": False,
            "keywords": False,
            "category": False,
            "comments_num": False,
            },
            self.__class__.__name__,
            non_empty=True,
        )


    def extract(self, response: str, metadata: PipeMetadata) -> Dict[Any, Any] | None:
        return super().extract(response, metadata)

    def extract_soup(self, soup: BeautifulSoup, metadata: PipeMetadata):
        extracted_dict = self.article_extract(soup, metadata)
        if not self.required_check_fc(extracted_dict, metadata):
            return None

        metadata.name = metadata.domain_record.url.replace("/", "_")[:80]
        extracted_dict["url"] = metadata.domain_record.url
        extracted_dict["domain_record"] = metadata.domain_record.model_dump()
        return extracted_dict

    def custom_filter_raw(self, response: str, metadata: PipeMetadata) -> bool:
        return True

    def custom_filter_soup(self, soup: BeautifulSoup, metadata: PipeMetadata) -> bool:
        return True

    def filter_raw(self, response: str, metadata: PipeMetadata) -> bool:
        if metadata.http_header.get("http_response_code", 200) != 200:
            metadata_logger.warn(
                f"Invalid Status: {metadata.http_header.get('http_response_code', 0)}",
                extra={"domain_record": metadata.domain_record},
            )
            return False

        if self.custom_filter_raw(response, metadata) is False:
            return False
        return True

    def filter_soup(self, soup: BeautifulSoup, metadata: PipeMetadata) -> bool:
        if not must_exist_filter(soup, self.filter_must_exist):
            return False

        if not must_not_exist_filter(soup, self.filter_must_not_exist):
            return False

        if (
            self.filter_allowed_domain_prefixes is not None
            and metadata.url_parsed.netloc.split(".")[0]
            not in self.filter_allowed_domain_prefixes
        ):
            return False

        if self.custom_filter_soup(soup, metadata) is False:
            return False

        return True

    def article_extract(
        self, soup: BeautifulSoup, metadata: PipeMetadata
    ) -> Dict[Any, Any]:
        extracted_head = extract_transform(
            soup.select_one("head"), self.header_css_dict, self.header_extract_dict
        )

        extracted_article = extract_transform(
            soup.select_one(self.article_css_selector),
            self.article_css_dict,
            self.article_extract_dict,
        )

        custom_extract = self.custom_extract(soup, metadata)

        # merge dicts
        extracted_dict = combine_dicts(
            [extracted_head, extracted_article, custom_extract]
        )
        return extracted_dict

    def custom_extract(
        self, soup: BeautifulSoup, metadata: PipeMetadata
    ) -> Dict[str, Any]:
        # Allows for custom extraction of values
        return {}