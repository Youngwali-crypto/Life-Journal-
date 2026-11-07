"""Share a transaction across prototype stores without committing it early."""
import sqlite3
from contextlib import closing, contextmanager


@contextmanager
def database_session(path, connection=None):
    if connection is not None:
        yield connection
        return
    with closing(sqlite3.connect(path)) as owned_connection, owned_connection:
        yield owned_connection
