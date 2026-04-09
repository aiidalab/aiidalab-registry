#!/bin/bash

rm -rf build/
aiidalab registry build $@ \
	--templates=src/templates/ \
	--static=src/static/ \
	--out=build/
