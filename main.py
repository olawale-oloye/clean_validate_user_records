"""
Script to clean a list of user records and return clean and rejected records.

This module performs basic data validation and normalization on user records.
It validates email, age, and country fields, returning:
    - clean_records: validated and normalized records
    - rejected_records: invalid records with reasons for rejection

Logging is used to track processing progress and rejected records.

Designed to be compatible with:
    - mypy (static typing)
    - pylint (code quality)
    - flake8 (style compliance)
"""

from typing import Any, Dict, List, Optional, Tuple
from conf.conf import logger


def normalize_email(value: Any) -> Tuple[str, List[str]]:
    """
    Normalize and validate an email address.

    Steps performed:
        1. Ensure value is a string
        2. Trim whitespace
        3. Convert to lowercase
        4. Validate basic structure:
            - must contain '@'
            - must contain local part
            - must contain domain with a dot

    Args:
        value (Any):
            Raw email value from the input record.

    Returns:
        Tuple[str, List[str]]:
            normalized_email (str):
                Cleaned email string. Empty string if invalid.
            reasons (List[str]):
                List of validation errors encountered.
                Empty list indicates a valid email.
    """
    reasons: List[str] = []

    # Validate datatype
    if not isinstance(value, str):
        return "", ["email not a string"]

    # Normalize email format
    email = value.strip().lower()

    # Check for missing value
    if not email:
        return "", ["email missing"]

    # Basic structure validation
    if "@" not in email:
        reasons.append("email missing @")
    else:
        local, _, domain = email.partition("@")

        if not local:
            reasons.append("email missing local part")

        # Domain must exist and contain "."
        if not domain or "." not in domain:
            reasons.append("email domain invalid")

    return email, reasons


def parse_age(
    value: Any,
    *,
    min_age: int = 1,
    max_age: int = 119,
) -> Tuple[Optional[int], List[str]]:
    """
    Parse and validate an age value.

    Validation rules:
        - must be numeric
        - must fall within the specified range

    Args:
        value (Any):
            Raw age value from the input record.
        min_age (int, optional):
            Minimum allowed age (default = 1).
        max_age (int, optional):
            Maximum allowed age (default = 119).

    Returns:
        Tuple[Optional[int], List[str]]:
            age (Optional[int]):
                Parsed integer age if valid, otherwise None.
            reasons (List[str]):
                List of validation errors.
    """
    reasons: List[str] = []

    # Attempt numeric conversion
    try:
        age = int(value)
    except (TypeError, ValueError):
        return None, ["age not numeric"]

    # Validate age range
    if age < min_age or age > max_age:
        reasons.append("age out of range")

    return age, reasons


def normalize_country(value: Any) -> Tuple[str, List[str]]:
    """
    Normalize and validate a country value.

    Normalization:
        - trims whitespace
        - converts to uppercase

    Validation:
        - must be string
        - must not be empty
        - must not contain numeric characters

    Args:
        value (Any):
            Raw country value from the input record.

    Returns:
        Tuple[str, List[str]]:
            normalized_country (str):
                Uppercase country code/name.
                Empty string if invalid.
            reasons (List[str]):
                List of validation errors.
    """
    reasons: List[str] = []

    # Validate datatype
    if not isinstance(value, str):
        return "", ["country not a string"]

    # Normalize format
    country = value.strip().upper()

    # Validate presence
    if not country:
        return "", ["country missing"]

    # Detect invalid numeric characters
    if any(char.isdigit() for char in country):
        reasons.append("country contains numeric characters")

    return country, reasons


def clean_users(
    records: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Clean and validate a list of user records.

    Each record is validated using:
        - normalize_email()
        - parse_age()
        - normalize_country()

    Records with validation errors are stored separately
    along with the reason for rejection.

    Args:
        records (List[Dict[str, Any]]):
            List of user dictionaries expected to contain:
                email (str)
                age (str | int)
                country (str)

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:

        clean_records:
            List of validated and normalized records.

            Example:
            {
                "email": "user@example.com",
                "age": 35,
                "country": "US"
            }

        rejected_records:
            List of invalid records with reasons.

            Example:
            {
                "record": {...},
                "reasons": ["age out of range"]
            }
    """
    logger.info(
        "Starting user record cleaning: %s records received",
        len(records),
    )

    clean_records: List[Dict[str, Any]] = []
    rejected_records: List[Dict[str, Any]] = []

    # Iterate through each record
    for idx, record in enumerate(records, start=1):
        reasons: List[str] = []

        # Validate each field independently
        email, email_reasons = normalize_email(record.get("email"))
        age, age_reasons = parse_age(record.get("age"))
        country, country_reasons = normalize_country(record.get("country"))

        # Aggregate validation issues
        reasons.extend(email_reasons)
        reasons.extend(age_reasons)
        reasons.extend(country_reasons)

        # Reject record if any validation error occurs
        if reasons:
            logger.warning(
                "Record %s rejected | reasons=%s | record=%s",
                idx,
                reasons,
                record,
            )

            rejected_records.append(
                {
                    "record": record,
                    "reasons": reasons,
                }
            )
            continue

        # Append clean normalized record
        clean_records.append(
            {
                "email": email,
                "age": age,
                "country": country,
            }
        )

    logger.info(
        "Cleaning completed | clean=%s | rejected=%s",
        len(clean_records),
        len(rejected_records),
    )

    return clean_records, rejected_records


if __name__ == "__main__":
    # """
    # Example usage of the cleaning pipeline.

    # Demonstrates:
    #     - valid records
    #     - invalid records
    #     - logging output
    #     - rejected reason capture
    # """

    new_records = [
        {"email": "Ada@Example.com ", "age": "23", "country": "ng"},
        {"email": "Bold@Example.com ", "age": "23", "country": "0"},
        {"email": "", "age": "190", "country": "NG"},
        {"age": "0", "email": "bob@example.com", "country": "us"},
        {"age": "15", "email": "bob@.com", "country": ""},
        {"age": "35", "email": "@example.com", "country": "0"},
        {"age": "x", "email": "bob@example.com", "country": "CA"},
    ]

    clean, rejected = clean_users(new_records)

    print("Clean Data:", clean)
    # print("Rejected Data:", rejected)
