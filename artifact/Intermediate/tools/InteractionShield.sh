#!/bin/sh

# --- Step 1: Check if the user provided an argument ---
if [ -z "$1" ]; then
    echo "Error: Missing required argument."
    echo "Usage: $0 [Dataset|Example|Comparison]"
    echo "  Dataset:    Use the InteractionShield Dataset"
    echo "  Example:    Use the InteractionShield Example"
    echo "  Comparison: Use the Comparison Dataset"
    exit 1
fi

# Store the user's choice in a variable
CHOICE=$1

# --- Step 2: Set path variables based on the user's choice ---
case "$CHOICE" in
    Dataset)
        echo "==> Configuration selected: Dataset"
        DATASET_PATH="/InteractionShield/artifact/InteractionShield/Datasets/SmartThings"
        RESULT_PATH="/InteractionShield/artifact/InteractionShield/Files/Datasets"
        ;;

    Example)
        echo "==> Configuration selected: Example"
        DATASET_PATH="/InteractionShield/artifact/InteractionShield/Examples/SmartThings"
        RESULT_PATH="/InteractionShield/artifact/InteractionShield/Files/Examples"
        ;;

    Comparison)
        echo "==> Configuration selected: Comparison"
        DATASET_PATH="/InteractionShield/artifact/Intermediate/apps"
        RESULT_PATH="/InteractionShield/artifact/Intermediate/config"
        ;;

    *) # Handle invalid arguments
        echo "Error: Invalid argument '$1'."
        echo "Valid arguments are: [Dataset|Example|Comparison]"
        exit 1
        ;;
esac

# --- Step 3: Perform the common compilation steps ---
echo "==> Compiling Groovy and Java files..."
mkdir -p classes
groovyc -d classes /InteractionShield/artifact/InteractionShield/Groovy/org/codehaus/groovy/ast/expr/NotExpression.java /InteractionShield/artifact/InteractionShield/Groovy/SmartThingsHelper.groovy /InteractionShield/artifact/InteractionShield/Groovy/SmartThingsMain.groovy

# Check if compilation was successful
if [ $? -ne 0 ]; then
    echo "!!! Compilation failed. Aborting script. !!!"
    rm -rf classes
    exit 1
fi
echo "Compilation successful."
echo ""


# --- Step 4: Run the Groovy program using the path variables set earlier ---
echo "==> Running the main program..."
echo "    --dataset: $DATASET_PATH"
echo "    --result:  $RESULT_PATH"
groovy -cp classes /InteractionShield/artifact/InteractionShield/Groovy/SmartThingsMain.groovy --dataset "$DATASET_PATH" --result "$RESULT_PATH"


# --- Step 5: Clean up compiled files ---
echo ""
echo "==> Cleaning up the classes directory..."
rm -rf classes
echo "==> Task complete."
