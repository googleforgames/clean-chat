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
    echo -e "${RED}${1}${REG}"
}

yellow() {
    echo -e "${YELLOW}${1}${REG}"
}

green() {
    echo -e "${GREEN}${1}${REG}"
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
            printf " => %-30s %56s\n" "\"$COMMAND\"..." "[ $(green $PATH_TO_CMD) ]"
        else
            COMMANDS_OK=false
            MASTER_OK=false
            PATH_TO_CMD="$(red '-- MISSING --')"
        fi
    done
}

DEBIAN_OK=false
check_debian() {
    PACKAGES_OK=true
    MISSING_PACKAGES=""

    for PKG in $@; do
        
        SYSPKG=$(dpkg-query -W -f='${binary:Package}==${Version}' $PKG 2> /dev/null)
        
        if [ $? -eq 0 ]; then
            printf " => %-30s %56s\n" "\"$PKG\"..." "[ $(green $SYSPKG) ]"
        
        else
            PACKAGES_OK=false
            MISSING_PACKAGES+="$PKG "
            printf " => %-30s %56s\n" "\"$PKG\"..." "[ $(red '-- MISSING --') ]"
        fi
    done

    if [ $PACKAGES_OK = false ]; then
        echo "You have one or more missing packages, would you like to install them?"
        echo -n "<y/N>: "
        read input
        
        if [[ $input == "Y" || $input == "y" ]]; then
            sudo apt install $MISSING_PACKAGES
            check_debian $@
        else
            error "You have chosen NOT to install system packages. This might not work."
        fi
    fi

    DEBIAN_OK=true
}

LINUX_OK=false
check_linux() {

    if [ -r /etc/os-release ]; then
        source /etc/os-release

        if [[ $ID == "debian" ]]; then
            LINUX_OK="true"
        fi
    fi

	ID=$(yellow $ID)

    if [ $LINUX_OK = false ]; then
        printf " => %-30s %56s\n" "Debian or Crostini..." "[ $ID ]" #"[ $(yellow "$ID") ]"
        error "Your Linux distribution is unsupported, but might work."
        echo "Ensure these packages are installed: python3-pyaudio python3-termcolor portaudio"
        echo ""
    fi
}

PIP_OK=true
check_pips() {

    for LIB in $@; do
        PIPLIB=$(pip3 freeze | grep $LIB)

        if [ $? = 0 ]; then
            PIPLIB=$(green $PIPLIB)
        else
            PIP_OK=false
            MASTER_OK=false
            PIPLIB="$(red '-- MISSING --')"
        fi

        printf " => %-30s %56s\n" "\"$LIB\"..." "[ $PIPLIB ]"
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

check_os() { 
    if [[ "$OSTYPE" == "darwin"* ]]; then
        error "macOS is not supported due to issues with Port Audio and
        secure microphone access. Sorry!"
        exit 1
    elif [[ "$OSTYPE" == "linux-gnu" ]]; then
        printf " => %-35s %51s\n" "GNU/Linux..." "[ $(green $OSTYPE) ]"
    else
        error "Your operating system is not supported or detected. Sorry!"
        exit 1
    fi
}

# =============================================================================
# Sanity Checking: Binaries
# =============================================================================

echo ""
echo "Checking operating system..."
echo "================================================================================"
check_os
check_linux

echo ""
echo "Checking for requisite binaries..."
echo "================================================================================"
check_commands hostnamectl lscpu grep python3 pip3 docker gcloud
echo ""

if [ $COMMANDS_OK = false ]; then
    error "Please install the missing binaries/symlinks before continuing."
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
# Sanity Checking: Libraries
# =============================================================================

echo ""
echo "Checking for requisite system libraries..."
echo "================================================================================"
if [ $LINUX_OK = true ]; then
	check_debian python3-pyaudio python3-termcolor python3-requests python3-pip
else
	echo "Unable to check your system as it is unsupported."
fi

echo ""
echo "Checking for requisite Python libraries..."
echo "================================================================================"
check_pips PyAudio termcolor google-cloud-speech

if [ $PIP_OK = false ]; then
    error "Please install the missing Python libraries 
    before continuing."
fi

# =============================================================================
# Sanity Checking: gcloud stuff
# =============================================================================

# TODO: Check/print the current project.

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

if [ $MASTER_OK = false ]; then
    error "Errors were detected, exiting."
    exit 1
fi

echo ""
echo "Your current project is: >> $GCP_PROJECT <<"
echo ""

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
ENABLED_ANY=1

for REQUIRED_API in $REQUIRED_APIS; do
	if [ $(grep -q $REQUIRED_API <(echo $GCP_CURRENT_APIS))$? -eq 0 ]; then
		# It's already enabled:
        printf " => %-30s %56s\n" "\"$REQUIRED_API\"..." "[ $(green ON) ]"
	else
		# It needs to be enabled:
        printf " => %-30s %56s\n" "\"$REQUIRED_API\"..." "[ $(red OFF) ]"
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
