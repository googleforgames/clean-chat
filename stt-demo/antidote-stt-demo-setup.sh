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
    echo -e ${YELLOW}${1}${REG}
}

green() {
    echo -e "${GREEN}${1}${REG}"""
}

# Any errors encountered which require user intervention?
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
        PATH_TO_CMD="-- $(red MISSING) --"
    fi

	printf " => %-20s %66s\n" "\"$TESTCOMMAND\"..." "[ $(green $PATH_TO_CMD) ]"
}

CROSTINI=false
AUDIO_OK=true
check_audio() {
    EXTRALIB="[audio-libraries]"
    PKG="$(yellow '-- Unknown --')"

    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        
        if [ -f /etc/os-release ]; then
            source /etc/os-release
            if [[ $ID == "debian" ]]; then

                EXTRALIB="python3-pyaudio"
                SYSPKG=$(dpkg-query -W -f='${binary:Package}==${Version}' python3-pyaudio 2> /dev/null)
                if [ $? -eq 0 ]; then
                    PKG=$(green $SYSPKG)
                else
                    PKG=$(red '-- MISSING --')
                    printf " => %-20s %66s\n" "\"$EXTRALIB\"..." "[ $PKG ]"
                    echo "You are missing the Debian package \"python3-pyaudio\"."
                    echo -n "Would you like to install it? <y/N>: "
                    read input
                    
                    if [[ $input == "Y" || $input == "y" ]]; then
                        sudo apt install python3-pyaudio
                        
                        SYSPKG=$(dpkg-query -W -f='${binary:Package}==${Version}' python3-pyaudio 2> /dev/null)
                        PKG=$(green $SYSPKG)
                        printf " => %-20s %66s\n" "\"$EXTRALIB\"..." "[ $PKG ]"
                    else
                        AUDIO_OK=false
                    fi
                fi

                # Best guess ChromeOS's Crostini here:
                hostnamectl status | grep Virtualization | grep -q lxc && lscpu | grep Hypervisor | grep -q KVM
                if [ $? -eq 0 ]; then
                    CROSTINI=true
                    printf " => %-35s %54s\n" "\"Crostini Microphone Access\"..." "[ $(yellow '¯\_(ツ)_/¯') ]"
                fi
            else
                printf " => %-20s %64s\n" "\"$EXTRALIB\"..." "[ $PKG ]"
                error "Your Linux distribution is unsupported, but might work."
                echo "You should be able to install \"python3-pyaudio\" and \"portaudio\" or their equivalents."
            fi

        else
            printf " => %-20s %64s\n" "\"$EXTRALIB\"..." "[ $PKG ]"
            error "Your Linux distribution is missing /etc/os-release, sorry!"
            echo "You should be able to install \"python3-pyaudio\" and \"portaudio\" or their equivalents."
        fi

    # Note: Darwin is unsupported on recent versions due to issues with PortAudio.
    else
        printf " => %-20s %64s\n" "\"$EXTRALIB\"..." "[ $PKG ]"
        error "macOS is not supported due to issues with Port Audio and
        secure microphone access. Sorry!"
        exit 1
    fi

}

PIP_OK=true
check_pip() {
	TESTLIB=$1
	PIPLIB=$(pip3 freeze | grep $TESTLIB)

    if [ $? = 0 ]; then
        PIPLIB=$(green $PIPLIB)
    else
        PIP_OK=false
        MASTER_OK=false
        PIPLIB="$(red '-- MISSING --')"
    fi

	printf " => %-20s %66s\n" "\"$TESTLIB\"..." "[ $PIPLIB ]"
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

    printf " => %-20s %66s\n" "\"$VAR\"..." "[ $PARAM ]"
}

CREDS_OK=true
check_default_creds() {
    TOKEN=$(green OK)

    if [[ $GCP_AUTHTOKEN == *"ERROR"* ]]; then
        CREDS_OK=false
        MASTER_OK=false
        TOKEN="-- $(red MISSING) --"
    fi

    printf " => %-32s %50s\n" "\"application-default credentials\"..." "[ $TOKEN ]"
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
check_command gcloud
check_command python3
check_command pip3
check_command docker
echo ""

if [ $COMMANDS_OK = false ]; then
    error "Please install the missing binaries/symlinks before continuing."
    exit 1
fi

# =============================================================================
# Sanity Checking: Libraries
# =============================================================================

echo ""
echo "Checking for requisite libraries..."
echo "================================================================================"
check_audio
sync
check_pip PyAudio
check_pip termcolor


if [ $AUDIO_OK = false ]; then
    error "Please install the system-specific libraries before continuing."
    exit 1
fi

if [ $CROSTINI = true ]; then
    echo ""
    echo "                    $(yellow '==> You appear to be using Crostini! <==')"
    echo "    $(yellow "Double-check that you've enabled microphone sharing in ChromeOS settings!")"
    echo ""
fi

if [ $PIP_OK = false ]; then
    error "Please install the missing Python libraries 
    before continuing."
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

if [ $MASTER_OK = false ]; then
    error "Errors were detected, exiting."
    exit 1
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
ENABLED_ANY=1

for REQUIRED_API in $REQUIRED_APIS; do
	if [ $(grep -q $REQUIRED_API <(echo $GCP_CURRENT_APIS))$? -eq 0 ]; then
		# It's already enabled:
        printf " => %-20s %66s\n" "\"$REQUIRED_API\"..." "[ $(green ON) ]"
	else
		# It needs to be enabled:
        printf " => %-20s %66s\n" "\"$REQUIRED_API\"..." "[ $(red OFF) ]"
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