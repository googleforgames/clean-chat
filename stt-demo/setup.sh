#/usr/bin/env bash
# Antidote Speech-to-Text Demo Setup
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
# Libraries and Functions
# =============================================================================

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
REG="\033[0m"

red() {
    echo -e "${RED}${@}${REG}"
}

yellow() {
    echo -e "${YELLOW}${@}${REG}"
}

green() {
    echo -e "${GREEN}${@}${REG}"
}

# Attribute Print, prints in the format, works with colors:
# ================================================================================
# => "thing"                                                            [ stauts ]
attrprint() {
    printf " => %-40s %46s\n" "\"$1\"..." "[ $2 ]"
}

# Any errors encountered which require user intervention?
MASTER_OK=true

# Prefixes output and writes to STDERR:
error() {
	echo -e "\n\nAntidoteSTT Error: $@\n" >&2
}

# Checks for command presence in $PATH, errors:
COMMANDS_OK=true
check_commands() {
    for COMMAND in $@; do
        PATH_TO_CMD=$(command -v $COMMAND)
        if [ $? = 0 ]; then
            attrprint $COMMAND "$(green $PATH_TO_CMD)"
        else
            COMMANDS_OK=false
            attrprint $COMMAND "$(red -- MISSING --)"
        fi
    done
}

# Checks to see if gcloud configs are (unset):
GCLOUD_CONFIG_OK=true
check_unset() {
	PARAM=$(green $1)
	VAR=$2
    
    if [[ $PARAM == *"(unset)"* ]]; then
        GCLOUD_CONFIG_OK=false
        MASTER_OK=false
        PARAM="$(red '-- UNSET --')"
	fi

    printf " => %-30s %56s\n" "\"$VAR\"..." "[ $PARAM ]"
}

# FIXME/TODO: Fix this to check proper creds, as speech no longer works with ADC:
CREDS_OK=true
check_default_creds() {
    TOKEN=$(green OK)

    if [[ $GCP_AUTHTOKEN == *"ERROR"* ]]; then
        CREDS_OK=false
        MASTER_OK=false
        TOKEN="-- $(red MISSING) --"
    fi

    printf " => %-40s %46s\n" "\"application-default credentials\"..." "[ $TOKEN ]"
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
# Sanity Checking: Binaries
# =============================================================================

echo ""
echo "Checking for requisite binaries..."
echo "================================================================================"
check_commands docker hostnamectl lscpu gcloud grep go make rec upx
echo ""

if [ $COMMANDS_OK = false ]; then
    error "Please install the missing binaries before continuing."
    exit 1
fi

# Are we running on ChromeOS's Crostini?
hostnamectl status | grep Virtualization | grep -q lxc && lscpu | grep Hypervisor | grep -q KVM
if [ $? -eq 0 ]; then
    CROSTINI=true
    echo "                         [38;5;000m [38;5;000m [38;5;000m [38;5;000m [38;5;000m [38;5;008m/[38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m/[38;5;000m [38;5;000m [38;5;000m [38;5;000m [38;5;000m 
                         [38;5;000m [38;5;000m [38;5;000m [38;5;009m/[38;5;009m/[38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m([38;5;009m/[38;5;009m/[38;5;009m/[38;5;009m/[38;5;000m [38;5;000m 
                         [38;5;000m [38;5;000m [38;5;006m*[38;5;008m*[38;5;009m/[38;5;009m/[38;5;009m/[38;5;009m([38;5;009m([38;5;009m([38;5;015m@[38;5;015m@[38;5;015m@[38;5;015m@[38;5;015m@[38;5;015m@[38;5;011m([38;5;011m([38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;000m 
                         [38;5;000m [38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;009m/[38;5;009m/[38;5;009m/[38;5;015m@[38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;015m@[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#
                         [38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;009m*[38;5;015m@[38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;006m/[38;5;015m@[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#
                         [38;5;000m [38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;015m@[38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;014m([38;5;006m/[38;5;014m([38;5;015m@[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#
                         [38;5;000m [38;5;000m [38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;015m@[38;5;015m@[38;5;015m@[38;5;015m@[38;5;015m@[38;5;015m@[38;5;006m,[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;000m 
                         [38;5;000m [38;5;000m [38;5;000m [38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m,[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;000m [38;5;000m 
                         [38;5;000m [38;5;000m [38;5;000m [38;5;000m [38;5;000m [38;5;000m [38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m*[38;5;006m,[38;5;006m,[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;011m#[38;5;000m [38;5;000m [38;5;000m [38;5;000m [38;5;000m [0m"
    echo ""
    echo "                    $(yellow '==> You appear to be using Crostini! <==')"
    echo "    $(yellow "Double-check that you've enabled microphone sharing in ChromeOS settings!")"
    echo "                        $(yellow "This must be done on each boot.")"
    echo ""
fi

# =============================================================================
# Sanity Checking: gcloud stuff
# =============================================================================

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

if [ $GCLOUD_CONFIG_OK = false ]; then
    error "Please ensure all gcloud variables are set via:
    gcloud config set <variable> <value>"
fi

if [ $CREDS_OK = false ]; then
    error "Please set the default credentials via:
    gcloud auth application-default login"
fi

# =============================================================================
# Sanity Checking: APIs
# =============================================================================

# Note: if the project variable is unset, this will not work. Proceed *only* if
# if the rest of the gcloud section is valid.

echo ""
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
MISSING_APIS=false

for REQUIRED_API in $REQUIRED_APIS; do
	if [ $(grep -q $REQUIRED_API <(echo $GCP_CURRENT_APIS))$? -eq 0 ]; then
        attrprint $REQUIRED_API "$(green ON)"
	else
        attrprint $REQUIRED_API "$(red OFF)"
		enable_api $REQUIRED_API.googleapis.com &
		MISSING_APIS=true
	fi
done

# If we've enabeld any API, wait for child processes to finish:
if [ $MISSING_APIS = true ]; then
    echo ""
    echo "You had one or more APIs disabled. Please wait while they are enabled."
    echo "Would you like to enable them?"
    echo -n "<Y/n> : "
    read choice
    if [ $choice != y ]; then
        exit 1
    fi
	printf '%-72s' " Concurrently enabling APIs..."
	wait
    echo "[ Done ]"
fi

# =============================================================================
# Configure Docker
# =============================================================================

echo ""
echo "Checking and configuring Docker..."
echo "================================================================================"

MYGROUPS=$(groups)
if [[ "$MYGROUPS" == *"docker"* ]]; then
    echo "You are a Dockerer."
fi

# =============================================================================
# Build the binary
# =============================================================================

echo ""
echo "Building the binary..."
echo "================================================================================"

make

# =============================================================================
# You're all set!
# =============================================================================

# 0x6a j ┘
# 0x6b k ┐
# 0x6c l ┌
# 0x6d m └
# 0x6e n ┼
# 0x71 q ─
# 0x74 t ├
# 0x75 u ┤
# 0x76 v ┴
# 0x77 w ┬
# 0x78 x │

echo ""
echo "┌──────────────────────────────────────────────────────────────────────────────┐"
echo "│                             YOUR SYSTEM IS READY                             │"
echo "└──────────────────────────────────────────────────────────────────────────────┘"