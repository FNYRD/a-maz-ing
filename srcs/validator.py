from typing import Dict, Any, Tuple


class ConfigParser():
    """Receives a config file, reads it, parses and validates its data."""

    def __init__(self, config_file: str) -> None:
        self.config_file = config_file

    def read_config(self) -> Dict[str, str]:
        """Tries to open the config file and returns Key=Value pairs as a Dict"""
        
        config_data: Dict[str, str] = {}
        try:
            with open(self.config_file, "r") as config_file:
                for line_num, line in enumerate(config_file, 1):
                    line = line.strip()

                    if not line or line.startswith('#'):
                        continue

                    if '=' in line:
                        key, value = line.split("=", 1)
                        
                        # are we accepting spaces??????????????????????????????
                        config_data[key.strip()] = value.strip()
                    else:
                        raise SyntaxError(f"wrong syntax in line [{line_num}]")
            return config_data

        except FileNotFoundError:
            print(f"Error: config file '{self.config_file}' not found")
        except PermissionError:
            print(f"Error: config file '{self.config_file}' is not accesible")
        except OSError:
            print(f"Error: an error ocurred while opening config file '{self.config_file}'")
        except SyntaxError as e:
            print(f"Error: {e} - Values must be in 'KEY=VALUE' format")


class Validator():
    """Class that handles validation of config data"""

    def validate_config(self, input_data: Dict[str, str]) -> Dict[str, Any]:
        """Validates the config data provided is valid to run the program,
        performes all the type conversions required"""
        
        def parse_coords(coord_str: str) -> Tuple[int, int]:
            """Gets (x,y) coordinates as a string, validates the format,
            and returns them as a tuple"""

            values: List[str] = coord_str.split(',')
            if len(values) != 2:
                raise SyntaxError("coordinates should be in 'KEY=x,y' format")
            return tuple((int(values[0]), int(values[1])))

        required: List[str] = ["WIDTH", "HEIGHT", "ENTRY",
                               "EXIT", "OUTPUT_FILE", "PERFECT"]
        output_data: Dict[str, Any] = {}

        # Verifying all requiered keys are present
        for key in required:
            if key not in input_data.keys():
                raise KeyError(f"Missing requiered configuration value {key}")
        
        # check if width is valid:
        try:
            output_data["WIDTH"] = int(input_data["WIDTH"])
            if output_data["WIDTH"] < 2:
                raise ValueError("Minimal 'WIDTH' value: 2")
        except ValueError as e:
            raise ValueError(f"Wrong 'WIDTH' value ({e})")

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

        return output_data
