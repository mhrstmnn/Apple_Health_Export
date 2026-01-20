import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

from .globals import (
    DATA_FILE_PATH,
    JSON_INDENT,
    get_argparse_description,
    get_output_file_path,
)


def parse_health_export() -> tuple[list[dict[str, str]], list[str]]:
    records: list[dict[str, str]] = []
    record_types: list[str] = []

    for _, elem in ET.iterparse(DATA_FILE_PATH):
        if elem.tag == "Record":
            records.append(elem.attrib)
            if elem.attrib["type"] not in record_types:
                record_types.append(elem.attrib["type"])

    return records, record_types


def print_all_record_types(record_types: list[str]):
    print(json.dumps(record_types, indent=JSON_INDENT))


def write_all_records_json_file(records: list[dict[str, str]]):
    with open(get_output_file_path("all_records", "json", "jq"), "w") as json_file:
        json_file.write(json.dumps(records, indent=JSON_INDENT) + "\n")


def write_all_records_txt_file(records: list[dict[str, str]]):
    with open(get_output_file_path("all_records", "txt", "jq"), "w") as txt_file:
        for record in records:
            txt_file.write(json.dumps(record) + "\n")


def write_all_records_csv_file_with_jq():
    cat_command = f"cat {get_output_file_path('all_records', 'txt', 'jq')}"
    jq_command = 'jq -r "[.type, .creationDate, .startDate, .endDate, .value, .unit, .device, .sourceName, .sourceVersion] | @csv"'
    output_file_path = get_output_file_path("all_records", "csv", "jq")
    subprocess.run(f"{cat_command} | {jq_command} > {output_file_path}", shell=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=get_argparse_description("JSON and CSV files"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--print-types",
        help="whether all record types should be printed",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        "--write-json",
        help="whether all records JSON file should be written",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--write-csv",
        help="whether all records CSV file should be written with jq",
        action="store_true",
    )

    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()
        return 0

    cli_options = {
        "print_all_record_types": args.print_types,
        "write_all_records_json_file": args.write_json,
        "write_all_records_csv_file": args.write_csv,
    }

    records, record_types = parse_health_export()

    if cli_options["print_all_record_types"]:
        print("All record types:\n")
        print_all_record_types(record_types)
        return 0

    if cli_options["write_all_records_json_file"]:
        print("All records JSON file is being written …")
        write_all_records_json_file(records)

    if cli_options["write_all_records_csv_file"]:
        print("All records text file is being written …")
        write_all_records_txt_file(records)
        print("All records CSV file is being written with jq …")
        write_all_records_csv_file_with_jq()

    return 0


if __name__ == "__main__":
    sys.exit(main())
