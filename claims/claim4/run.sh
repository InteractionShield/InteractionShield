#!/bin/sh

INTER_DIR=/InteractionShield/artifact/InteractionShield
FILES_DIR="$INTER_DIR/Files"
ARCHIVE=/opt/InteractionShield.tar.gz

if [ ! -d "$FILES_DIR" ] || [ -z "$(ls -A "$FILES_DIR")" ]; then
  tar -xzf "$ARCHIVE" -C "$INTER_DIR"
fi

cd /InteractionShield/artifact/InteractionShield
python3 -m Python.artifact.performance 500
python3 -m Python.artifact.plot_performance
cd /InteractionShield
