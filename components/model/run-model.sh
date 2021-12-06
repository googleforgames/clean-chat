#/usr/bin/env bash
# Antidote Model Wrapper Script

echo "
               ___        __  _    __     __        
              / _ | ___  / /_(_)__/ /__  / /____   
             / __ |/ _ \/ __/ / _  / _ \/ __/ -_)   
            /_/ |_/_//_/\__/_/\_,_/\___/\__/\__/    
                                                                    
"

echo "                      Welcome to the Antidote Model Service"
echo ""

# =============================================================================
# Main
# =============================================================================


read -p "Would you like to train, test, or deploy a model?: " x
echo "Running ${x}"
echo "================================================================================"
python model_trainer.py


