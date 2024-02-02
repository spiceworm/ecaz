import random
from typing import List

from random_username.generate import generate_username

from application.models import User


def csv_to_list(csv: str, delimiter: str = ",") -> List[str]:
    return [s.strip() for s in csv.split(delimiter)]


def generate_unique_username(id_range=100_000):
    username = generate_username()[0]
    while User.query.filter_by(username=username).one_or_none():  # pragma: no cover
        number = random.randint(0, id_range)
        username = f"{username}{number}"
    return username
