import sys
import os
from typing import Dict, Any, Tuple


def read_config(config_file: str) -> Dict[str, str]:
    """Tries to open the config file and returns Key=Value pairs as a Dict"""
    
    config_data: Dict = {}
    try:
        with open(sys.argv[1], "r") as config_file:
            for line_num, line in enumerate(config_file, 1):
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split("=", 1)
                    # are we accepting spaces?
                    config_data[key.strip()] = value.strip()
                else:
                    raise SyntaxError(f"wrong syntax in line [{line_num}]")
        return config_data

    except FileNotFoundError:
        print(f"Error: config file '{sys.argv[1]}' not found")
    except PermissionError:
        print(f"Error: config file '{sys.argv[1]}' is not accesible")
    except OSError:
        print(f"Error: an error ocurred while opening config file '{sys.argv[1]}'")
    except SyntaxError as e:
        print(f"Error: {e} - Values must be in 'KEY=VALUE' format")


def parse_coords(coord_str: str) -> Tuple[int, int]:
    """Gets (x,y) coordinates as a string, validates the format,
    and returns them as a tuple"""

    values: List[str] = coord_str.split(',')
    if len(values) != 2:
        raise SyntaxError("coordinates should be in 'KEY=x,y' format")
    return tuple((int(values[0]), int(values[1])))


def validate_config(input_data: Dict[str, str]) -> Dict[str, Any]:
    """Validates the config data provided is valid to run the program,
    performes all the type conversions required"""

    required: List[str] = ["WIDTH", "HEIGHT", "ENTRY",
                           "EXIT", "OUTPUT_FILE", "PERFECT"]
    output_data: Dict[str, Any] = {}

    for key in required:
        if key not in config_data.keys():
            raise KeyError(f"Missing requiered configuration value {key}")
    
    # check if width is valid:
    try:
        output_data["WIDTH"] = int(input_data["WIDTH"])
        if output_data["WIDTH"] < 2:
            raise ValueError("Minimal 'WIDTH' value: 2")
    except ValueError as e:
        raise ValueError("Wrong 'WIDTH' value ({e})")

    # check if height is valid:
    try:
        output_data["HEIGHT"] = int(input_data["HEIGHT"])
        if output_data["HEIGHT"] < 2:
            raise ValueError("Minimal 'HEIGHT' value: 2")
    except ValueError as e:
        raise ValueError(f"Wrong 'HEIGHT' value ({e})")

    # check if entry and exit coordinates are valid and parse them into a tuple
    for key in required[2:4]:
        try:
            output_data[key]: Tuple[int, int] = parse_coords(input_data[key])
            x, y = output_data[key]
            if x < 0 or x > output_data["WIDTH"]:
                raise ValueError(f"X value out of bounds: '{x}'")
            if y < 0 or y > output_data["HEIGHT"]:
                raise ValueError(f"Y value out of bounds: '{y}'")
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Wrong value for {key} coordinates ({e})")

    # checks that output filename is valid:
    output_data["OUTPUT_FILE"] = input_data["OUTPUT_FILE"]
    if not output_data["OUTPUT_FILE"]:
        raise ValueError(f"Output filename is empty!")
    if len(output_data["OUTPUT_FILE"]) > 100:
        raise ValueError(f"Wrong output filename (too long!)")

    # check for valid boolen values for PERFECT key:
    if input_data["PERFECT"].upper() == "TRUE":
        output_data["PERFECT"]: bool = True
    elif input_data["PERFECT"].upper() == "FALSE":
        output_data["PERFECT"]: bool = False
    else:
        raise ValueError("PERFECT only accepts boolean values (TRUE/FALSE)")


if __name__ == "__main__":

    # check if we have a config filename
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} [config file]")
        exit(1)
    
    config_data: Dict[str, Any] = read_config(sys.argv[1])
    if not config_data:
        exit(1)
    
    try:
        config_data = validate_config(config_data)
    except (KeyError, ValueError) as e:
        print("Configuration Error:", e)
        exit(1)
