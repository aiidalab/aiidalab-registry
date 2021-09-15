#!/bin/bash

aiidalab registry build $@ \
	--templates=src/templates/ \
	--static=src/static/ \
	--out=build/
