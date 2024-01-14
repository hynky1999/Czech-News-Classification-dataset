import argparse
import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
import random
from cmoncrawl.middleware.stompware import StompProcessor
from cmoncrawl.processor.pipeline.streamer import StreamerFileJSON
from cmoncrawl.processor.pipeline.downloader import AsyncDownloader
from cmoncrawl.processor.dao.api import CCAPIGatewayDAO
from cmoncrawl.processor.pipeline.pipeline import ProcessorPipeline
from cmoncrawl.integrations.extract import create_router, load_config
from cmoncrawl.common.loggers import all_purpose_logger


@asynccontextmanager
async def construct_pipeline(config_path: Path, max_retry: int, sleep_step: int, output_path: Path, max_directory_size: int, max_file_size: int):
    config = load_config(config_path)
    router = create_router(config)
    dao = CCAPIGatewayDAO()
    await dao.aopen()
    yield ProcessorPipeline(
        router=router,
        downloader=AsyncDownloader(max_retry=max_retry, sleep_base=sleep_step, dao=dao),
        outstreamer=StreamerFileJSON(root=output_path, max_directory_size=max_directory_size, max_file_size=max_file_size),
    )
    await dao.aclose()





def get_hostname_output_path(output_path: Path):
    hostname = os.environ["HOSTNAME"]
    if hostname == "":
        hostname = f"default{random.randint(0, 100)}"
        all_purpose_logger.warning(
            f"HOSTNAME is not set using hostname: {hostname}"
        )

    return output_path / hostname

    

def get_args():
    parser = argparse.ArgumentParser(description="Processor")
    parser.add_argument(
        "config_path",
        type=Path,
    )
    parser.add_argument("addresses", type=str, nargs="+")
    parser.add_argument("--queue_host", type=str, default="artemis")
    parser.add_argument("--queue_port", type=int, default=61616)
    parser.add_argument("--queue_size", type=int, default=80)
    parser.add_argument("--pills_to_die", type=int, default=None)
    parser.add_argument("--output_path", type=Path, default=Path("output"))
    parser.add_argument("--use_hostname_output", action="store_true")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--max_retry", type=int, default=20)
    parser.add_argument("--sleep_step", type=int, default=15)
    return parser.parse_args()

async def run():
    args = get_args()
    if args.use_hostname_output:
        args.output_path = get_hostname_output_path(args.output_path)

    async with construct_pipeline(config_path=args.config_path, max_retry=args.max_retry, sleep_step=args.sleep_step, output_path=args.output_path, max_directory_size=5000, max_file_size=100_000) as pipeline:
        processor = StompProcessor(
            queue_host=args.queue_host,
            queue_port=args.queue_port,
            queue_size=args.queue_size,
            pills_to_die=args.pills_to_die,
            pipeline=pipeline,
            timeout=args.timeout,
            addresses=args.addresses,
        )

        await processor.process()

if __name__ == "__main__":
    asyncio.run(run())
