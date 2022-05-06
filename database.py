'''
    The module contains the function of forming the configuration object of
    connection to the database from file and the initial objects to create and
    work with it.
'''

import pathlib
from operator import itemgetter

import yaml
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR / "database_connection.yaml"


def get_config(path: pathlib.Path):
    '''
        Forms datatase connection config from YAML file.
    '''

    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def create_connection_url(config: dict):
    '''
        Creates database connection string, for example:
          "postgresql+asyncpg://postgres:admin@localhost/database"
    '''

    props = ("dbms", "driver", "user", "password", "host", "port", "name")

    prop_getter = itemgetter(*props)

    dbms, driver, user, password, host, port, name = prop_getter(config)

    url = f"{dbms}+{driver}://{user}:{password}@{host}:{port}/{name}"

    return url


config = get_config(config_path)

DATABASE_CONNECTION_URL = create_connection_url(config["database"])

engine = create_async_engine(DATABASE_CONNECTION_URL, echo=True)

Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
