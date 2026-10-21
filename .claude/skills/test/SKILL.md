---
name: test
description: Adds or fixes tests - the test pyramid, one behaviour per test, negative paths for boundaries, and never weakening an assertion to make a test pass. Use when adding behaviour, fixing a bug (first a failing test), or when a test fails.
---

# Test

## Overview
A test proves a behaviour; a weakened test proves nothing. Most tests are fast unit tests; a few integration tests cover real boundaries.

## When to use
Every behaviour change; every bug fix (write the failing test first); every failing test.

## Process
1. Name the behaviour in the test's name, in plain words.
2. Arrange, act, assert one thing. Use real inputs over mocks where cheap.
3. For an access boundary: missing and wrong credentials, a forbidden route, hostile input.
4. Prove the test can fail: run it against the old code, or break the code once.
5. A failing test: find the cause; fix the code, or the test only if the test was wrong — and say why.

## Rationalizations
| Excuse | Rebuttal |
| --- | --- |
| "The assertion is too strict" | Then the requirement changed: update the spec first. |
| "It's flaky" | Flaky is a bug with a timing cause. Find it. |

## Red flags
Assertions removed in a fix; tests that only check that nothing threw; skipped tests left behind.

## Verification
- [ ] The new test failed before the change and passes after.
- [ ] No assertion was weakened without a spec change.
