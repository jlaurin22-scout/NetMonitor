#!/bin/bash

set -e

source "$(dirname "$0")/installer/common.sh"
source "$(dirname "$0")/installer/packages.sh"
source "$(dirname "$0")/installer/users.sh"
source "$(dirname "$0")/installer/directories.sh"
source "$(dirname "$0")/installer/launcher.sh"
source "$(dirname "$0")/installer/service.sh"
source "$(dirname "$0")/installer/web_permissions.sh"
source "$(dirname "$0")/installer/auth.sh"
source "$(dirname "$0")/installer/restart.sh"
source "$(dirname "$0")/installer/verify.sh"


print_header

require_root

select_installation_type

prepare_installation

install_packages

install_users

create_directories

install_launcher

install_service

install_web_permissions

install_authentication

restart_service

verify_installation