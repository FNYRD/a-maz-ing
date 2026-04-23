import sys
from typing import Dict, Any, Tuple
from srcs.validator import ConfigParser, Validator
from srcs.manager import MazeManager


def main():
    # check if we have a config filename
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} [config file]")
        exit(1)
    
    # open file and parse data:
    parser: ConfigParser = ConfigParser(sys.argv[1])
    config_data: Dict[str, str] = parser.read_config()
    if not config_data:
        exit(1)

    validator: Validator = Validator()
    try:
        manager: MazeManager = MazeManager(validator.validate_config(config_data))
    except (KeyError, ValueError) as e:
        print("Configuration Error:", e)
        exit(1)


if __name__ == "__main__":
    main()
