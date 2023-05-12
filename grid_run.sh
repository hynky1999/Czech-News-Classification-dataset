#!/bin/bash
INDEXORS=('idnes.cz' 'aktualne.cz' 'novinky.cz' 'denik.cz' 'seznamzpravy.cz' 'irozhlas.cz' 'ihned.cz')
# INDEXORS=('idnes.cz')
PYTHON_PATH="/opt/python/3.10.4/bin/python3"
ARTEMIS_HOST="cpu-node3"
ARTEMIS_PORT="61602"
HTTP_PORT="6100"
ARTEMIS_MEMORY_MAX="64g"

CUR_DIR="$(realpath "$(dirname "$0")")"
AGG_EXEC="${CUR_DIR}/aggregate.sh"
PROC_EXEC="${CUR_DIR}/process.sh"
PROCESSOR_PATH="${CUR_DIR}/Processor"
AGGREGATOR_PATH="${CUR_DIR}/Aggregator"
ARTEMIS_PATH="$CUR_DIR/Artemis"
ARTEMIS_RUN_PATH=$ARTEMIS_PATH/run_artemis
EXC="sbatch"
PROCESSORS_NUM="$((2 * ${#INDEXORS[@]}))"
# PROCESSORS_NUM=1
# If fresh start =1 then all Artemis data will be deleted
# -> duplicates will be forgotten and data lost.
# Good for testing.
FRESH_START=1

#Artemis
# $EXC -o artemis.log -w "$ARTEMIS_HOST" \
# --cpus-per-task=4 \
# --mem="$ARTEMIS_MEMORY_MAX" \
# "$ARTEMIS_PATH/create_artemis.sh" \
# "$ARTEMIS_PATH" \
# "$ARTEMIS_RUN_PATH" \
# "0.0.0.0" \
# "$ARTEMIS_PORT" \
# "$HTTP_PORT" \
# "$ARTEMIS_MEMORY_MAX" \
# "$FRESH_START"

# Aggregators
# ENV_PATH="$AGGREGATOR_PATH/env"
# if [[ ! -e "$ENV_PATH" ]]; then
#     "$PYTHON_PATH" -m venv "$ENV_PATH"
#     "$ENV_PATH/bin/pip3" install -r "$AGGREGATOR_PATH/requirements.txt"
# fi

# for index in "${INDEXORS[@]}"; do
#     $EXC \
#     --mem=1g \
#     --cpus-per-task=1 \
#     -o "aggregator_$index.log" "$AGG_EXEC" "$AGGREGATOR_PATH" \
#     --queue_host="$ARTEMIS_HOST" \
#     --queue_port=$ARTEMIS_PORT \
#     --max_retry=100 \
#     --sleep_step=15 \
#     "$index"
# done


ENV_PATH="$PROCESSOR_PATH/env"
if [[ ! -e "$ENV_PATH" ]]; then
    "$PYTHON_PATH" -m venv "$ENV_PATH"
    "$ENV_PATH/bin/pip3" install -r "$PROCESSOR_PATH/requirements.txt"
fi


# queues create
for element in "${INDEXORS[@]}"
do
  modified_element="queue.${element}"
  queues+=("${modified_element}")
done
echo "${queues[@]}"


for ((i=15; i < "$(($PROCESSORS_NUM + 15))"; ++i)); do
    $EXC \
    --mem=1g \
    --cpus-per-task=1 \
    -o "processor_$i.log" \
    "$PROC_EXEC" "$PROCESSOR_PATH" \
    --queue_host="$ARTEMIS_HOST" \
    --pills_to_die="${#INDEXORS[@]}" \
    --queue_port="$ARTEMIS_PORT" \
    --output_path="$(realpath "./output_${i}")" \
    --timeout=360 \
    --max_retry=100 \
    --sleep_step=15 \
    "$PROCESSOR_PATH/config.json" \
    "${queues[@]}"


done









