#!/bin/sh

INTER_DIR=/InteractionShield/artifact/InteractionShield
FILES_DIR="$INTER_DIR/Files"
ARCHIVE=/opt/InteractionShield.tar.gz

if [ ! -d "$FILES_DIR" ] || [ -z "$(ls -A "$FILES_DIR")" ]; then
  tar -xzf "$ARCHIVE" -C "$INTER_DIR"
fi

sh /InteractionShield/artifact/Intermediate/tools/generate_random_smartapps.sh 25 5

mkdir -p /InteractionShield/artifact/IoTSan/output/IotSanOutput/birc

python3 /InteractionShield/artifact/Intermediate/tools/run_iotsan.py

python3 /InteractionShield/artifact/Intermediate/tools/run_iotcom.py

cd /InteractionShield/artifact/InteractionShield
python3 -m Python.artifact.comparison
python3 -m Python.artifact.plot_comparison

find . -maxdepth 1 -regextype posix-extended -regex '.*\/pan(\.[a-z])?|.*\/SmartThings[0-9]+\.prom\.trail' -delete
