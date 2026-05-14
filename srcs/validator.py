from typing import Dict, Any, Tuple, List


class ConfigParser():
    """Receive a config file, read it and parse its data."""

    def __init__(self, config_file: str) -> None:
        """Initialize the parser.

        config_file: name of the text file containing maze parameters.
        """
        self.config_file = config_file

    def read_config(self) -> Dict[str, str] | None:
        """Try to open the config file and return Key=Value as a Dict

        Return a dictionary containing the parameters in the config file.
        Return None on failure to read the file, printing the cause.
        """

        config_data: Dict[str, str] = {}
        try:
            with open(self.config_file, "r") as config_file:
                for line_num, line in enumerate(config_file, 1):
                    line = line.strip()

                    if not line or line.startswith('#'):
                        continue

                    if '=' in line:
                        key, value = line.split("=", 1)
                        config_data[key.strip()] = value.strip()
                    else:
                        raise SyntaxError(f"wrong syntax in line [{line_num}]")
            return config_data

        except FileNotFoundError:
            print(f"Error: config file '{self.config_file}' not found")
        except PermissionError:
            print(f"Error: config file '{self.config_file}' is not accesible")
        except OSError:
            print("Error: an error ocurred while opening config file"
                  f" '{self.config_file}'")
        except SyntaxError as e:
            print(f"Error: {e} - Values must be in 'KEY=VALUE' format")
        return None


class Validator():
    """Class to handle validation of config data"""

    def validate_config(self, input_data: Dict[str, str]) -> Dict[str, Any]:
        """Check if the config data is valid and convert it to right type

        input_data: dicitionary with configuration parameter to validate.
        Return a dictionary with clean data for maze generator class.
        If anything fail, raise the correspondeing exception.
        """

        def parse_coords(coord_str: str) -> Tuple[int, int]:
            """Gets (x,y) coordinates as a string and validates the format

            coord_str: x,y coordinates to parse
            Returns the coordinates as a tuple, raises an exception on fail
            """

            values: List[str] = coord_str.split(',')
            if len(values) != 2:
                raise SyntaxError("coordinates should be in 'KEY=x,y' format")
            return ((int(values[0]), int(values[1])))

        required: List[str] = ["WIDTH", "HEIGHT", "ENTRY",
                               "EXIT", "OUTPUT_FILE", "PERFECT"]
        optional: List[str] = ["SEED", "ALT_ALGORITHM"]
        output_data: Dict[str, Any] = {}

        # Verifying all requiered keys are present
        for key in required:
            if key not in input_data.keys():
                raise KeyError(f"Missing requiered configuration value {key}")

        # check that all keys are valid:
        for key in input_data.keys():
            if key not in required and key not in optional:
                raise KeyError(f"Invalid configuration parameter '{key}'")

        # check if width and heigth are valid:
        for key in required[0:2]:
            try:
                output_data[key.lower()] = int(input_data[key])
                if output_data[key.lower()] < 2:
                    raise ValueError(f"Minimal {key} value: 2")
                if output_data[key.lower()] > 40:
                    raise ValueError(f"Maximun {key} value: 40")
            except ValueError as e:
                raise ValueError(f"Wrong {key} value ({e})")

        # check if entry and exit coords are valid and parse them into a tuple
        for key in required[2:4]:
            try:
                output_data[key.lower()] = parse_coords(input_data[key])
                x, y = output_data[key.lower()]
                if x < 0 or x >= output_data["width"]:
                    raise ValueError(f"X value out of bounds: '{x}'")
                if y < 0 or y >= output_data["height"]:
                    raise ValueError(f"Y value out of bounds: '{y}'")
            except (ValueError, SyntaxError) as e:
                raise ValueError(
                        f"Wrong value for {key} coordinates ({e})")
        if output_data["entry"] == output_data["exit"]:
            raise ValueError("ENTRY and EXIT must be different!")

        # checks that output filename is valid:
        output_data["output_file"] = input_data["OUTPUT_FILE"]
        if not output_data["output_file"]:
            raise ValueError("Output filename is empty!")
        if len(output_data["output_file"]) > 100:
            raise ValueError("Wrong output filename (too long!)")

        # check for valid boolen values for PERFECT/ALT_ALGORITHM key:
        if "ALT_ALGORITHM" not in input_data.keys():
            input_data["ALT_ALGORITHM"] = "FALSE"
        for key in ["PERFECT", "ALT_ALGORITHM"]:
            if key in input_data:
                if input_data[key].upper() == "TRUE":
                    output_data[key.lower()] = True
                elif input_data[key].upper() == "FALSE":
                    output_data[key.lower()] = False
                else:
                    raise ValueError(
                            f"{key} only accepts boolean values (TRUE/FALSE)")

        # verifies if seed is an int:
        if "SEED" in input_data.keys():
            try:
                output_data["seed"] = int(input_data["SEED"])
            except ValueError as e:
                raise ValueError(f"Wrong 'SEED' value ({e})")

        return output_data
