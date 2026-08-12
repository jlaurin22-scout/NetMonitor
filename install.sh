#!/bin/bash

source "$(dirname "$0")/installer/common.sh"
source "$(dirname "$0")/installer/packages.sh"
source "$(dirname "$0")/installer/directories.sh"
source "$(dirname "$0")/installer/launcher.sh"
source "$(dirname "$0")/installer/service.sh"
source "$(dirname "$0")/installer/restart.sh"
source "$(dirname "$0")/installer/verify.sh"

require_root

print_header

echo "Repository : $PROJECT_DIR"
echo

select_installation_type
prepare_installation

install_packages
create_directories
install_launcher
install_service
restart_service
verify_installation

echo "Installer completed successfully."

exit 0
