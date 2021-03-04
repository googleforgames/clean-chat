#/usr/bin/env bash
# Antidote Speech-to-Text Demo Wrapper Script
# Sebastian Weigand <tdg@google.com>

echo "
               ___        __  _    __     __        ________________
              / _ | ___  / /_(_)__/ /__  / /____   / __/_  __/_  __/
             / __ |/ _ \/ __/ / _  / _ \/ __/ -_) _\ \  / /   / /   
            /_/ |_/_//_/\__/_/\_,_/\___/\__/\__/ /___/ /_/   /_/    
                                                                    
"

echo "                      Welcome to Antidote Speech to Text!"
echo ""

# =============================================================================
# Main
# =============================================================================

echo ""
echo "Running the Antidote Docker container..."
echo "================================================================================"
docker run --name="antidote-stt" --rm -d -p 8501:8501 gcr.io/antidote-playground/antidote-stt:v1

echo ""
echo "Running the STT server..."
echo "================================================================================"
rec --channels=1 --bits=16 --rate=16k --type=raw --no-show-progress - | ./antidote-stt-demo

echo ""
echo ""
echo "Stopping the Antidote Docker container..."
docker kill antidote-stt
echo ""