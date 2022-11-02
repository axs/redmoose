import argparse
import json
import logging
import os
import sys

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

desc = """
Creates the sd. if it doesnt exist it will create
cd to red-moose root
alembic upgrade head
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-d", "--drop", help="drop database", action="store_true")
parser.add_argument("-c", "--create", help="create database", action="store_true")
parser.add_argument("-a", "--alembic_migrate", help="create tables", action="store_true")
parser.add_argument("-n", "--name", help="name of database", default="sd")
args = parser.parse_args()

log.info(f"Arguments: {args}")

CONF_DIR = os.path.join(os.path.dirname(__file__), "../../conf")
conf = json.load(open(f"{CONF_DIR}/postgres.json"))

con = psycopg2.connect(dbname='postgres',
                       user=conf.get('user'),
                       host=conf.get('host'),
                       port=conf.get('port'),
                       password=conf.get('password'))

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = con.cursor()

if args.drop:
    log.info(f"Dropping database {args.name}")
    cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
        sql.Identifier(args.name))
    )

if args.create:
    log.info(f"Creating database {args.name}")
    cur.execute(sql.SQL("CREATE DATABASE {}").format(
        sql.Identifier(args.name))
    )


if args.alembic_migrate:
    log.info(f"Creating tables")
    ALEMBIC_DIR = os.path.join(os.path.dirname(__file__), "../../")

    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config(f"{ALEMBIC_DIR}/alembic.ini")
    alembic_cfg.set_main_option('script_location', f"{ALEMBIC_DIR}/alembic")
    command.upgrade(alembic_cfg, "head")

