#!/bin/bash

set -o errexit

set -o pipefail

set -o nounset

python << END

import sys
import time
import psycopg2

suggest_unrecoverable_after=30
start=time.time()
while True:
    try:
        psycopg2.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}",
        )
        break
    except psycopg2.OperationalError as error:
        sys.stderr.write("waiting for PostgreSQL to become available. \n")
        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write(f"This is taking longer than expected. The following error may be indicative of unrecoverable error: '{error}'.\n")
        time.sleep(3)

END

echo >&2 'PostgreSQL is available.'

exec "$@"
