from __future__ import annotations

from pathlib import Path

from . import core


def main() -> None:
    args = core.parse_config_arg()
    result = core.run_execution(Path(args.config))
    print(result["verdict"])


if __name__ == "__main__":
    main()
