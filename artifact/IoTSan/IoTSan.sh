#!/bin/bash

mkdir -p bin

CLASSPATH_LIBS="lib/bandera:lib/bcel:lib/soot:lib/java_cup:lib/groovy-3.0.0-alpha-3/lib/groovy-3.0.0-alpha-3.jar:lib/ant.jar:lib/castor.jar:lib/CCK.jar:lib/gef.jar:lib/log4j.jar:lib/openjgraph.jar:lib/Regex.jar:lib/xerces.jar:lib/jpf-core/build/jpf.jar:lib/excel/commons-codec-1.10.jar:lib/excel/commons-collections4-4.1.jar:lib/excel/commons-logging-1.2.jar:lib/excel/curvesapi-1.04.jar:lib/excel/junit-4.12.jar:lib/excel/log4j-1.2.17.jar:lib/excel/poi-3.16.jar:lib/excel/poi-excelant-3.16.jar:lib/excel/poi-ooxml-3.16.jar:lib/excel/poi-ooxml-schemas-3.16.jar:lib/excel/poi-scratchpad-3.16.jar:lib/excel/xmlbeans-2.6.0.jar:lib/jsoup-1.11.2.jar:lib/json-simple-1.1.jar"

find src -name "*.java" > source_files.tmp

if [ ! -s source_files.tmp ]; then
    echo "No .java files found in src directory. Nothing to compile."
else
    javac -d bin -cp "$CLASSPATH_LIBS" @source_files.tmp

    if [ $? -ne 0 ]; then
        echo ""
        echo "!!! COMPILE FAILED !!!"
        rm source_files.tmp
        exit 1
    fi
fi
rm source_files.tmp

find src -name "*.dat" | while read f; do
    target="bin/${f#src/}"
    mkdir -p "$(dirname "$target")"
    cp "$f" "$target"
done

echo "Compilation successful."

echo ""
echo "--- Step 2: Running the application ---"

RUN_CP="bin:$CLASSPATH_LIBS"

java -cp "$RUN_CP" IotSan

echo ""
echo "--- Done ---"
