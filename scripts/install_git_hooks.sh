#!/usr/bin/env bash

set -x

pre-commit install --hook-type pre-commit
pre-commit install --hook-type commit-msg
