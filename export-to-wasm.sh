#!/usr/bin/env bash
mkdir wasm
marimo export html-wasm arcanecodex.py -o ./wasm --mode run
