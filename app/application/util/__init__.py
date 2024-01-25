from typing import List


def csv_to_list(csv: str, delimiter: str = ",") -> List[str]:
    return [s.strip() for s in csv.split(delimiter)]
