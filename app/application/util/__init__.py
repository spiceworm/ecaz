from typing import List

from random_username.generate import generate_username


def csv_to_list(csv: str, delimiter: str = ",") -> List[str]:
    return [s.strip() for s in csv.split(delimiter)]


def generate_random_username() -> str:
    return generate_username()[0]
