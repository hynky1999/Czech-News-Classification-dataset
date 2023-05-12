import sys
from pathlib import Path

# Since it loads everything in CZExtrators, init will also be executed
# This is a hack to add the parent directory to sys.path
# Otherwise there is no way to use the module while using the CLI
sys.path.append(str(Path(__file__).parent.parent))