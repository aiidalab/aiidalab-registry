#!/bin/bash

# Exit with nonzero exit code if anything fails and be verbose
set -ev

# Set paths
BUILD_PATH="${TRAVIS_BUILD_DIR}/make_ghpages"
DEPLOY_PATH="${TRAVIS_BUILD_DIR}/.travis-data"

# Make sure we're in the package root
cd ${TRAVIS_BUILD_DIR}

case "$RUN_TYPE" in
    tests)
        # Run pytest
        pytest
        ;;
    build)
        # Build pages
        python "$BUILD_PATH/make_pages.py"

        # Deploy
        "$DEPLOY_PATH/deploy.sh"
        ;;
esac
