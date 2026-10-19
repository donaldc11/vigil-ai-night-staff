#!/bin/sh
# test double: exit code from FAKE_SNYK_EXIT (0 clean, 1 vulns, 2 error)
echo '{"ok": false}'; exit ${FAKE_SNYK_EXIT:-0}
