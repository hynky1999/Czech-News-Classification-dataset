import argparse
from datetime import datetime
from cmoncrawl.middleware.stompware import StompAggregator
from cmoncrawl.aggregator.gateway_query import GatewayAggregator
from cmoncrawl.common.loggers import metadata_logger
from cmoncrawl.common.types import MatchType
import asyncio


def get_args():
    parser = argparse.ArgumentParser(description="Download articles")
    parser.add_argument("url", type=str)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--since", type=str, default=datetime.min)
    parser.add_argument("--to", type=str, default=datetime.max)
    parser.add_argument("--queue_host", type=str, default="artemis")
    parser.add_argument("--queue_port", type=int, default=61616)
    parser.add_argument("--cc_servers", nargs="+", type=str, default=[])
    parser.add_argument("--prefetch_size", type=int, default=2)
    parser.add_argument("--max_retry", type=int, default=20)
    parser.add_argument("--sleep_step", type=int, default=5)
    args = parser.parse_args()
    if isinstance(args.since, str):
        args.since = datetime.fromisoformat(args.since)

    if isinstance(args.to, str):
        args.to = datetime.fromisoformat(args.to)

    return args

def run():
    args = get_args()
    index_aggregator = GatewayAggregator(
        urls=[args.url],
        limit=args.limit,
        since=args.since,
        to=args.to,
        cc_servers=args.cc_servers,
        prefetch_size=args.prefetch_size,
        max_retry=args.max_retry,
        sleep_base=args.sleep_step,
        match_type=MatchType.DOMAIN
    )
    aggregator = StompAggregator(
        url=args.url,
        queue_host=args.queue_host,
        queue_port=args.queue_port,
        index_agg=index_aggregator,
    )

    asyncio.run(aggregator.aggregate(filter_duplicates=False))

if __name__ == "__main__":
    run()