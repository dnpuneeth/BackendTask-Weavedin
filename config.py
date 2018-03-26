from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


CONFIG = [
    'root',                          # Username
    'password',                              # Password
    'localhost',                     # Host
    'inventorydb'        # Database Name
]
engine = create_engine(
    "mysql://{0}:{1}@{2}/{3}".format(CONFIG[0], CONFIG[1], CONFIG[2], CONFIG[3])
)
Session = sessionmaker(bind=engine)
session = Session()
