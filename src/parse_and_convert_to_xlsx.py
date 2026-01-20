import argparse
import sys
import xml.etree.ElementTree as ET

import pandas as pd

from .globals import DATA_FILE_PATH, get_argparse_description, get_output_file_path

pd.options.mode.copy_on_write = True


def parse_health_export() -> tuple[pd.DataFrame, list[str]]:
    tree = ET.parse(DATA_FILE_PATH)
    root = tree.getroot()

    records = [element.attrib for element in root.iter("Record")]
    records_df = pd.DataFrame(records)

    date_columns = ["creationDate", "startDate", "endDate"]
    for date_column in date_columns:
        records_df[date_column] = pd.to_datetime(
            records_df[date_column]
        ).dt.tz_localize(None)

    record_types: list[str] = records_df["type"].unique().tolist()

    return records_df, record_types


def to_snake_case(string: str) -> str:
    return "".join(
        ["_" + char.lower() if char.isupper() else char for char in string]
    ).removeprefix("_")


def type_identifier_to_name(type_identifier: str) -> str:
    for prefix in [
        "HKQuantityTypeIdentifier",
        "HKCategoryTypeIdentifier",
        "HKDataType",
    ]:
        type_identifier = type_identifier.removeprefix(prefix)
    return to_snake_case(type_identifier)


def print_all_record_types(record_types: list[str]):
    for count, record_type in enumerate(record_types):
        print(f"{count + 1}: {record_type} -> {type_identifier_to_name(record_type)}")


def write_all_records_excel_file(
    records_df: pd.DataFrame,
    rearranged: bool = False,
):
    filename = "all_records"
    if rearranged:
        filename += "_rearranged"
    file_path = get_output_file_path(filename, "xlsx")
    print(f'Write all records Excel file to: "{file_path}"')
    records_df.to_excel(file_path)  # pyright: ignore[reportUnknownMemberType]


def write_blood_pressure_excel_file(
    rearranged_records_df: pd.DataFrame,
    reduce_output: bool,
):
    blood_pressure_systolic_df = rearranged_records_df.query(
        'type == "HKQuantityTypeIdentifierBloodPressureSystolic"'
    )
    if reduce_output:
        blood_pressure_systolic_df.drop(columns=["type", "unit"], inplace=True)
    else:
        blood_pressure_systolic_df.drop(
            columns=["type", "unit", "device", "sourceName", "sourceVersion"],
            inplace=True,
        )

    blood_pressure_diastolic_df = rearranged_records_df.query(
        'type == "HKQuantityTypeIdentifierBloodPressureDiastolic"'
    )
    blood_pressure_diastolic_df.drop(
        columns=["type", "startDate", "endDate"], inplace=True
    )

    merged_blood_pressure_df = pd.merge(
        blood_pressure_systolic_df, blood_pressure_diastolic_df, on="creationDate"
    )
    merged_blood_pressure_df.rename(
        columns={"value_x": "valueSystolic", "value_y": "valueDiastolic"}, inplace=True
    )

    file_path = get_output_file_path("blood_pressure", "xlsx")
    print(f'Write blood pressure Excel file to: "{file_path}"')
    merged_blood_pressure_df.to_excel(file_path)  # pyright: ignore[reportUnknownMemberType]


def write_all_other_excel_files(
    record_types: list[str],
    rearranged_records_df: pd.DataFrame,
):
    # Remove blood pressure record types
    for record_type in [
        "HKQuantityTypeIdentifierBloodPressureSystolic",
        "HKQuantityTypeIdentifierBloodPressureDiastolic",
    ]:
        if record_type in record_types:
            record_types.remove(record_type)

    for record_type in record_types:
        filtered_records_df = rearranged_records_df.query(f'type == "{record_type}"')
        filtered_records_df.drop(columns="type", inplace=True)

        if record_type.startswith("HKCategoryTypeIdentifier"):
            filtered_records_df.drop(columns="unit", inplace=True)

        record_name = type_identifier_to_name(record_type)
        file_path = get_output_file_path(record_name, "xlsx")
        print(f'Write {record_name.replace("_", " ")} Excel file to: "{file_path}"')
        filtered_records_df.to_excel(file_path)  # pyright: ignore[reportUnknownMemberType]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=get_argparse_description("Excel files"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--print-types",
        help="whether all record types should be printed",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--one-file",
        help="whether all records should be written to one Excel file",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--separate-files",
        help="whether all records should be written to separate Excel files",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--reduce-output",
        help="whether to reduce output when writing Excel files",
        action="store_true",
    )

    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()
        return 0

    cli_options = {
        "print_all_record_types": args.print_types,
        "write_all_records_excel_file": args.one_file,
        "write_all_other_excel_files": args.separate_files,
        "reduce_output": args.reduce_output,
    }

    if sum(vars(args).values()) == 1 and cli_options["reduce_output"]:
        print(
            "info: the option to reduce output has no effect if no Excel files are being written"
        )
        return 0

    records_df, record_types = parse_health_export()

    if cli_options["print_all_record_types"]:
        print("All record types:\n")
        print_all_record_types(record_types)
        return 0

    if cli_options["reduce_output"]:
        rearranged_records_df = records_df[
            ["type", "creationDate", "startDate", "endDate", "value", "unit"]
        ]
    else:
        rearranged_records_df = records_df[
            [
                "type",
                "creationDate",
                "startDate",
                "endDate",
                "value",
                "unit",
                "device",
                "sourceName",
                "sourceVersion",
            ]
        ]

    if cli_options["write_all_records_excel_file"]:
        print("All records Excel files are being written:\n")
        write_all_records_excel_file(records_df)
        write_all_records_excel_file(rearranged_records_df, True)
        if cli_options["write_all_other_excel_files"]:
            print("\n")

    if cli_options["write_all_other_excel_files"]:
        print("All other Excel files are being written:\n")
        write_blood_pressure_excel_file(
            rearranged_records_df, cli_options["reduce_output"]
        )
        write_all_other_excel_files(record_types, rearranged_records_df)

    return 0


if __name__ == "__main__":
    sys.exit(main())
