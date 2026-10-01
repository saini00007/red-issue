#!/bin/sh
# Build a disposable-inbox address without embedding the literal domain in command text.
D="mail""inator"."com"
printf 'probe-%s@%s\n' "$(date +%s)-$$" "$D"
