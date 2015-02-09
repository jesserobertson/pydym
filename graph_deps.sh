#!/usr/bin/env bash
# file:   graph_dependencies.sh
# author: Jess Robertson
#         CSIRO Minerals Resources National Research Flagship
# date:   10 July 2014
#
# description: Uses snakefood to graph Python dependencies for the given library

NAME=pydym
ROOT="./${NAME}"
PDF="${NAME}.pdf"

sfood "${ROOT}" | sfood-graph | dot -Tps | ps2pdf - $@ > "${PDF}"