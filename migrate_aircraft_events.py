import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIR / "flightwatch.db"
BACKUP_DIR = PROJECT_DIR / "backups"

OLD_COLUMNS = {
    "id",
    "registration",
    "aircraft_type",
    "event_type",
    "callsign",
    "latitude",
    "longitude",
    "timestamp",
}

NEW_COLUMNS = {
    "id",
    "icao24",
    "event_type",
    "callsign",
    "latitude",
    "longitude",
    "timestamp",
}


def get_table_columns(connection, table_name):
    rows = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return {
        row["name"]
        for row in rows
    }


def create_backup():
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    backup_path = BACKUP_DIR / (
        f"flightwatch-before-events-migration-{timestamp}.db"
    )

    shutil.copy2(
        DATABASE_PATH,
        backup_path
    )

    return backup_path


def normalize_registration(value):
    if not value:
        return None

    return str(value).strip().upper()


def normalize_icao24(value):
    if not value:
        return None

    return str(value).strip().lower()


def load_registration_map(connection):
    columns = get_table_columns(
        connection,
        "aircraft_metadata"
    )

    if not {
        "registration",
        "icao24"
    }.issubset(columns):
        return {}

    rows = connection.execute(
        """
        SELECT
            registration,
            icao24
        FROM aircraft_metadata
        WHERE registration IS NOT NULL
          AND icao24 IS NOT NULL
        """
    ).fetchall()

    registration_map = {}

    for row in rows:
        registration = normalize_registration(
            row["registration"]
        )

        icao24 = normalize_icao24(
            row["icao24"]
        )

        if registration and icao24:
            registration_map[registration] = icao24

    return registration_map


def migrate_aircraft_events(connection):
    columns = get_table_columns(
        connection,
        "aircraft_events"
    )

    if not columns:
        print(
            "aircraft_events does not exist. "
            "No migration was performed."
        )
        return False

    if NEW_COLUMNS.issubset(columns):
        print(
            "aircraft_events already uses the ICAO24 schema. "
            "No migration is needed."
        )
        return False

    if not OLD_COLUMNS.issubset(columns):
        raise RuntimeError(
            "aircraft_events has an unexpected schema: "
            + ", ".join(sorted(columns))
        )

    registration_map = load_registration_map(
        connection
    )

    old_rows = connection.execute(
        """
        SELECT
            id,
            registration,
            event_type,
            callsign,
            latitude,
            longitude,
            timestamp
        FROM aircraft_events
        ORDER BY id
        """
    ).fetchall()

    connection.execute(
        """
        CREATE TABLE aircraft_events_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icao24 TEXT,
            event_type TEXT,
            callsign TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
        """
    )

    mapped_count = 0
    unmapped_count = 0

    for row in old_rows:
        registration = normalize_registration(
            row["registration"]
        )

        icao24 = registration_map.get(
            registration
        )

        if icao24:
            mapped_count += 1
        else:
            unmapped_count += 1

        connection.execute(
            """
            INSERT INTO aircraft_events_new (
                id,
                icao24,
                event_type,
                callsign,
                latitude,
                longitude,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                icao24,
                row["event_type"],
                row["callsign"],
                row["latitude"],
                row["longitude"],
                row["timestamp"],
            )
        )

    connection.execute(
        "DROP TABLE aircraft_events"
    )

    connection.execute(
        """
        ALTER TABLE aircraft_events_new
        RENAME TO aircraft_events
        """
    )

    print(
        f"Migrated {len(old_rows)} event rows."
    )

    print(
        f"Mapped {mapped_count} rows to ICAO24."
    )

    print(
        f"Preserved {unmapped_count} rows "
        "with ICAO24 left blank."
    )

    return True


def verify_migration(connection):
    columns = get_table_columns(
        connection,
        "aircraft_events"
    )

    if not NEW_COLUMNS.issubset(columns):
        raise RuntimeError(
            "Migration verification failed. "
            "The expected ICAO24 schema was not created."
        )

    row_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM aircraft_events
        """
    ).fetchone()[0]

    return row_count


def main():
    if not DATABASE_PATH.exists():
        print(
            f"Database not found: {DATABASE_PATH}",
            file=sys.stderr
        )

        return 1

    backup_path = create_backup()

    print(
        f"Backup created: {backup_path}"
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    try:
        connection.execute(
            "PRAGMA foreign_keys = OFF"
        )

        connection.execute(
            "BEGIN IMMEDIATE"
        )

        changed = migrate_aircraft_events(
            connection
        )

        row_count = verify_migration(
            connection
        )

        connection.commit()

        if changed:
            print(
                "Migration completed successfully."
            )
        else:
            print(
                "Schema check completed successfully."
            )

        print(
            f"aircraft_events row count: {row_count}"
        )

        return 0

    except Exception as error:
        connection.rollback()

        print(
            f"Migration failed: {error}",
            file=sys.stderr
        )

        print(
            "The database transaction was rolled back. "
            f"Backup remains at: {backup_path}",
            file=sys.stderr
        )

        return 1

    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
