#!/bin/bash

LINK="https://nine.websudoku.com/?level=3"

LINES=$(curl ${LINK} 2>/dev/null | grep puzzle_grid | grep -P -o '<INPUT (.*?)>')

NUM=0

IFS=$'\n'
for line in ${LINES}; do
	if [[ $(echo ${line} | grep "VALUE") ]]; then
		VAL=$(echo -n ${line} | grep -Po "\"(.*?)\"" | cut -d '"' -f 2)
		echo -n "${VAL}"
	else
		echo -n '.'
	fi
	NUM=$((NUM+1))
	if [[ $((NUM % 9)) -eq 0 ]]; then
		echo
	fi
#	echo "line: ${line}"
done
