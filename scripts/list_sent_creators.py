"""List creators currently stored in the sent creator database."""

from __future__ import annotations

from automation_utils import db_connect, list_creators


def main() -> None:
    """Print all creator records."""
    connection = db_connect()
    try:
        rows = list_creators(connection)
        if not rows:
            print("No creators stored.")
            return

        for row_id, raw_name, normalized_name, sent_at in rows:
            print(f"{row_id}\t{sent_at}\t{normalized_name}\t{raw_name}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
