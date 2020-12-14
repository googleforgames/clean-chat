#/usr/bin/env bash
# Antidote Speech-to-Text Demo Setup
# Sebastian Weigand <tdg@google.com>

echo "
   ___        __  _    __     __        ________________
  / _ | ___  / /_(_)__/ /__  / /____   / __/_  __/_  __/
 / __ |/ _ \/ __/ / _  / _ \/ __/ -_) _\ \  / /   / /   
/_/ |_/_//_/\__/_/\_,_/\___/\__/\__/ /___/ /_/   /_/    
                                                        
"

echo "Welcome to the Antidote Speech-to-Text Demo!"
echo ""

# =============================================================================
# Libraries and Functions
# =============================================================================

MASTER_OK=true

# Prefixes output and writes to STDERR:
error() {
	echo -e "\n\nAntidoteSTT Error: $@\n" >&2
}

# Checks for command presence in $PATH, errors:
COMMANDS_OK=true
check_command() {
	TESTCOMMAND=$1
	PATH_TO_CMD=$(command -v $TESTCOMMAND)

    if [ $? = 1 ]; then
        COMMANDS_OK=false
        MASTER_OK=false
        PATH_TO_CMD="-- MISSING --"
    fi

	printf " => %-20s %55s\n" "\"$TESTCOMMAND\"..." "[ $PATH_TO_CMD ]"
}

# Checks to see if gcloud configs are (unset):
GCLOUD_CONFIG_OK=true
check_unset() {
	PARAM=$1
	VAR=$2
    
    if [[ $PARAM == *"(unset)"* ]]; then
        GCLOUD_CONFIG_OK=false
        MASTER_OK=false
        PARAM="-- UNSET --"
	fi

    printf " => %-20s %55s\n" "\"$VAR\"..." "[ $PARAM ]"
}

CREDS_OK=true
check_default_creds() {
    TOKEN="OK"

    if [[ $GCP_AUTHTOKEN == *"ERROR"* ]]; then
        CREDS_OK=false
        MASTER_OK=false
        TOKEN="-- MISSING --"
    fi

    printf " => %-32s %39s\n" "\"application-default credentials\"..." "[ $TOKEN ]"
}

# Returns just the value we're looking for OR unset:
gcloud_activeconfig_intercept() {
	gcloud $@ 2>&1 | grep -v "active configuration"
}

# Enables a single API:
enable_api() {
	gcloud services enable $1 >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		echo -e "\n  ! - Error enabling $1"
		exit 1
	fi
}

# =============================================================================
# Sanity Checking
# =============================================================================

echo ""
echo "Checking for requisite binaries..."
echo "================================================================================"
check_command gcloud
check_command python3
check_command docker
echo ""

# This executes all the gcloud commands in parallel and then assigns them to separate variables:
# Needed for non-array capabale bashes, and for speed.

echo ""
echo "Checking multiple gcloud variables in parallel..."
echo "================================================================================"
PARAMS=$(cat <(gcloud_activeconfig_intercept config get-value compute/zone) \
	<(gcloud_activeconfig_intercept config get-value compute/region) \
	<(gcloud_activeconfig_intercept config get-value project) \
	<(gcloud_activeconfig_intercept auth application-default print-access-token))
read GCP_ZONE GCP_REGION GCP_PROJECT GCP_AUTHTOKEN <<<$(echo $PARAMS)

# Check for our requisiste gcloud parameters:
check_unset $GCP_PROJECT "project"
check_unset $GCP_REGION "compute/region"
check_unset $GCP_ZONE "compute/zone"
check_default_creds $GCP_AUTHTOKEN

if [ $COMMANDS_OK = false ]; then
    error "Please install the missing binaries before continuing."
fi

if [ $GCLOUD_CONFIG_OK = false ]; then
    error "Please ensure all gcloud variables are set via:
    gcloud config set <variable> <value>"
fi

if [ $CREDS_OK = false ]; then
    error "Please set the default credentials via:
    gcloud auth application-default login"
fi

if [ $MASTER_OK = false ]; then
    error "Errors detected, exiting."
fi

echo ""

# =============================================================================
# Configure APIs
# =============================================================================

# List of requisite APIs:
REQUIRED_APIS="
	speech
"

# Bulk parrallel process all of the API enablement:
echo ""
echo "Checking requisite GCP APIs..."
echo "================================================================================"

# Read-in our currently enabled APIs, less the googleapis.com part:
GCP_CURRENT_APIS=$(gcloud services list | grep -v NAME | cut -f1 -d'.')

# Keep track of whether we modified the API state for friendliness:
ENABLED_ANY=1

for REQUIRED_API in $REQUIRED_APIS; do
	if [ $(grep -q $REQUIRED_API <(echo $GCP_CURRENT_APIS))$? -eq 0 ]; then
		# It's already enabled:
        printf " => %-20s %55s\n" "\"$REQUIRED_API\"..." "[ ON ]"
	else
		# It needs to be enabled:
        printf " => %-20s %55s\n" "\"$REQUIRED_API\"..." "[ OFF ]"
		enable_api $REQUIRED_API.googleapis.com &
		ENABLED_ANY=0
	fi
done

# If we've enabeld any API, wait for child processes to finish:
if [ $ENABLED_ANY -eq 0 ]; then
    echo ""
    echo "You had one or more APIs disabled. Please wait while they are enabled."
	printf '%-72s' " Concurrently enabling APIs..."
	wait
    echo "[ Done ]"
fi