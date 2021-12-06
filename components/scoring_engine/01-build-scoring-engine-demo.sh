# Remove/clean any existing container
docker rmi -f scoring_engine

# Build python dependency
python3 setup.py sdist

# Build scoring engine container
docker build --tag scoring_engine . 
