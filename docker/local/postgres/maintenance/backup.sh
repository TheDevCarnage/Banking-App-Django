#!/usr/bin/env bash

set -o errexit

set -o pipefail

set -o nounset

working_dir="$(dirname ${0})"

source "${working_dir}/_sourced/constants.sh"
source "${working_dir}/_sourced/messages.sh"

message_welcome "Backing up the '${POSTGRES_DB}' database..."

if [[ "${POSTGRES_USER}" == "postgres" ]]; then
  message_error "Backing up as 'postgres' user is not supported. Assign 'POSTGRES_USER' env with
  another one and try again."
  exit 1
fi

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD}"
export PGDATABASE="${POSTGRES_DB}"

backup_filename="${BACKUP_FILE_PREFIX}_$(date +'%Y_%m_%dT%H_%M_%S').sql.gz"

if ! pg_dump | gzip > "${BACKUP_DIR_PATH}/${backup_filename}"; then
  message_error "Database backup failed. Please check the PostgreSQL logs for more information."
  exit 1
fi

message_success "'${POSTGRES_DB}' database backup '${backup_filename}' has been created and
placed in the '${BACKUP_DIR_PATH}'"
