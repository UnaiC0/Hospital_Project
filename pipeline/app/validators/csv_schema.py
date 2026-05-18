from __future__ import annotations


class CsvSchemaError(ValueError):
    pass


def assert_columns_present(actual_columns: list[str], required_columns: tuple[str, ...]) -> None:
    missing = [column for column in required_columns if column not in actual_columns]
    if missing:
        raise CsvSchemaError(f"Missing required columns: {', '.join(missing)}")
