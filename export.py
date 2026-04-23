import json

from .locations import LOCATION_TABLE


def export_json() -> None:
    """Export location data to a JSON file."""
    # Very simple export used from /export_json command in the client.
    file_name = "locations-output.json"

    with open(file_name, "w") as file:
        file.write("[\n")
        for location, data in LOCATION_TABLE.items():
            json_str = json.dumps(
                {
                    "id": data.id,
                    "name": location,
                    "rules": data.rule.to_dict(),
                },
                indent=4,
                sort_keys=True,
            )
            file.write(f"{json_str},\n")
        file.write("]\n")
