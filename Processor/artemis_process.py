import argparse
from pathlib import Path
from cmoncrawl.middleware.stompware import ArtemisProcessor
from cmoncrawl.common.types import ExtractConfig
from cmoncrawl.processor.pipeline.streamer import StreamerFileJSON
from cmoncrawl.processor.pipeline.downloader import AsyncDownloader
from cmoncrawl.processor.pipeline.pipeline import ProcessorPipeline
from cmoncrawl.integrations.commands import


def construct_pipeine(config_path: Path):
    config = 
    router = create_router(config)

    

def get_args():
    parser = argparse.ArgumentParser(description="Processor")
    parser.add_argument("--queue_host", type=str, default="artemis")
    parser.add_argument("--queue_port", type=int, default=61616)
    parser.add_argument("--queue_size", type=int, default=80)
    parser.add_argument("--pills_to_die", type=int, default=None)
    parser.add_argument("--output_path", type=Path, default=Path("output"))
    parser.add_argument("--use_hostname_output", action="store_true")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--max_retry", type=int, default=20)
    parser.add_argument("--sleep_step", type=int, default=5)
    parser.add_argument(
        "--config_path",
        type=Path,
        default=Path(__file__).parent / "UserDefined" / "config.json",
    )


if __name__ == "__main__":
    parser = get_args()

    
    asyncio.run(processor(**vars(parser.parse_args())))