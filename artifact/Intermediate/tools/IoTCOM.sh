#!/bin/sh

rm -rf /InteractionShield/artifact/Intermediate/IoTCOM
mkdir -p /InteractionShield/artifact/Intermediate/IoTCOM

rm -rf /InteractionShield/artifact/Intermediate/als/
mkdir -p /InteractionShield/artifact/Intermediate/als/

cd /InteractionShield/artifact/IoTCOM/BehavioralRuleExtractor
mkdir -p bin
javac -d bin -cp "lib/*" $(find src -name "*.java")

java -cp "bin:lib/*" archExtractor.ToAlloy

cd /InteractionShield/artifact/IoTCOM/FormalAnalyzer
./gradlew customFatJar

# java -Xms32g -Xmx32g -XX:+UseG1GC -XX:MaxMetaspaceSize=1g -jar /InteractionShield/IoTCOM/FormalAnalyzer/build/libs/iotcom-all-1.0.0.jar --metadir /InteractionShield/IoTCOM/FormalAnalyzer/models/meta --appsdir /InteractionShield/Intermediate/als/ --outdir /InteractionShield/Intermediate/IoTCOM/ --template graph_model_general_template.ftl --bundlesizes 10
