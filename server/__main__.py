import sys
import common
from server.json_parser import Parser


def main(path: str) -> None:
    """
    Main function to process tasks and display them by device ID.
    """
    print(common.SERVER_MESSAGE)

    json_parser = Parser()

    data = json_parser.parse_json(path)

    if data is None:
        print("Error parsing JSON file")
        return None
    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m server <file_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    print(f"Processing tasks from file: {input_file}")
    main(input_file)
