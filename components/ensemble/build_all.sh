# Build Ensemble Container
docker rmi -f antidote_ensemble
docker build --tag antidote_ensemble ./ensemble/.

# Build Ensemble Container (for testing)
docker rmi -f antidote_ensemble_test
docker build --tag antidote_ensemble_test ./ensemble_test/.

# Build Simulators
docker rmi -f simulator_toxicity
docker rmi -f simulator_griefing
docker rmi -f simulator_cheat
docker build --tag simulator_toxicity ./simulator_toxicity/.
docker build --tag simulator_griefing ./simulator_griefing/.
docker build --tag simulator_cheat ./simulator_cheat/.

