from uuid import uuid4

from sqlalchemy import text

from domain.db import get_uow


def test_units_of_work_share_the_in_memory_database():
    table_name = f"memory_probe_{uuid4().hex}"

    try:
        with get_uow() as uow:
            uow.session.execute(
                text(f"CREATE TABLE {table_name} (value INTEGER NOT NULL)")
            )
            uow.session.execute(
                text(f"INSERT INTO {table_name} (value) VALUES (42)")
            )

        with get_uow() as uow:
            value = uow.session.execute(
                text(f"SELECT value FROM {table_name}")
            ).scalar_one()

        assert value == 42
    finally:
        with get_uow() as uow:
            uow.session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
