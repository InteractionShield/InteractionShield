#!/bin/sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <num_apps> <iters>"
    echo "Example: $0 15 10"
    exit 1
fi

NUM_APPS=$1
ITERS=$2

python3 /InteractionShield/artifact/Intermediate/tools/generate_random_smartapps.py
python3 /InteractionShield/artifact/Intermediate/tools/generate_app_bundles.py "${NUM_APPS}" "${ITERS}"
python3 /InteractionShield/artifact/Intermediate/tools/generate_iotsan_config.py

sh /InteractionShield/artifact/Intermediate/tools/InteractionShield.sh Comparison
