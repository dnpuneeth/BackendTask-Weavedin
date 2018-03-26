#!/usr/bin/env python

from sqlalchemy import create_engine


# If running as a script (i.e __name__ == "__main__"), add current directory to
# the python path so that relative imports work.
if __name__ == '__main__' and __package__ is None:
    import sys, os.path as path
    sys.path.append(path.dirname(path.abspath(__file__)))
    from config import CONFIG
    import models

    engine = create_engine(
        "mysql://{0}:{1}@{2}".format(CONFIG[0], CONFIG[1], CONFIG[2])
    )

    # Create database if required.
    with engine.connect() as connection:
        connection.execute("CREATE DATABASE IF NOT EXISTS {0}".format(CONFIG[3]))
        connection.execute("USE {0}".format(CONFIG[3]))
        
    # Creates all tables
    models.Base.metadata.create_all(engine)