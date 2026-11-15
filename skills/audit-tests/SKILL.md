---
name: audit-tests
description: Flags tests that test mocks, mock the project's own code, assert nothing meaningful, or skip the real stack, and lists behavior left untested. Use when the user runs /audit-tests or asks to audit or review the tests of a change.
disable-model-invocation: true
---

# Audit tests

Check whether the tests for a change would fail if the change were broken. A test that passes no matter what the production code does is worse than no test, because it gives false confidence.

Tests should run against the real stack, meaning whatever the project can run locally or in CI, such as its own modules, database, HTTP layer, and queues. Tests may mock or fake only third-party services that cost money, need credentials, or sit outside the project's control. Optimally we mock/fake at the network boundary.

This is a report. Do not edit code unless the user asks.

## Inputs

- **Target**: a PR or MR number or URL, a branch, or nothing (use the current branch against its base).
- **Allowed mocks**: third-party services the user names as mockable. If the user names none, treat any external paid or credentialed service as mockable, such as LLM APIs, payments, email, SMS, and cloud provider APIs. Say in the report which ones you assumed.

## Workflow

1. **Resolve the change.** For a PR use `gh pr view <n>` and `gh pr diff <n>`; for a GitLab MR use `glab mr view <n>` and `glab mr diff <n>`. Resolve its head and base revisions from the metadata and fetch them if needed. For a branch, use the requested branch as `<head>`; only use `HEAD` when no target was given. Determine `<base>` from the branch context or repository default, stating any assumption. Record both commit IDs and use `git diff <base>...<head>`. Read the description to learn what the change is meant to do. Read production code and tests from that same head, for example with `git show <head>:<path>`. Run tests only in a clean checkout of that revision; if unavailable, report a static audit and say execution was not verified. Preserve existing local work.
2. **Find the tests in scope.** Include tests added or changed in the diff, and existing tests that cover the changed functionality. To find them, search for the changed functions, routes, classes, and tables. Read the production code they cover, not just the diff.
3. **Learn what the real stack is.** Look at the test setup: fixtures, factories, test database, docker compose, testcontainers, test server, CI config. This tells you what tests could use. A test that mocks the database is a finding only if a real one is available or easy to add; say which.
4. **Audit each test.** Apply the checks below. For each suspect test, decide whether it would still pass if the code under test were broken.
5. **Prove the worst findings when practical.** In the clean target checkout:
   - Run the selected test unchanged first and confirm it executes and passes, rather than being skipped or selecting zero tests.
   - Break a behavior the test claims to cover, for example by inverting a condition, returning early, or dropping a write. Rebuild generated output and bypass caches as needed so the test executes the mutated code. If you cannot establish that, mark the check inconclusive.
   - Run the same test and report the exact mutation it missed. A surviving mutation demonstrates a specific coverage gap; it does not prove the test checks nothing or that the whole feature is untested. A failing baseline is also inconclusive.
   - Restore the edited file even if the run fails, using `git restore --source=<head> -- <file>`, and rebuild any affected output. Verify no mutation remains.
6. **List what is missing.** Compare the change's behavior to the tests: new branches, error paths, validation, permissions, edge cases, and migrations with no test.
7. **Report** in the format below.

## Checks

**Tests the mock**
- Asserts on a value the mock was configured to return, so the assertion only proves the mock works.
- Only asserts that a mock was called, with arguments the test itself just passed in.
- Stubs the unit under test, or part of it, then asserts on the stub.

**Mocks too much**
- Mocks the project's own modules, services, repositories, ORM, or database instead of using them.
- Mocks a third-party service above the network boundary, for example by patching the project's own client wrapper. The wrapper's request building and response parsing then go untested. Prefer a fake server, recorded responses, or the SDK's test mode.
- Uses a third-party fake whose data differs in shape from the real API, such as in fields, types, or error format. Check against the SDK types or API docs.
- Mocks heavily in a unit test where an integration test against the real stack is feasible.

**Asserts too little**
- Has no assertion, or asserts only that the code does not throw or returns something truthy.
- Checks the response status but not the body or the persisted state.
- Relies on a large snapshot that nobody would review when it changes.
- Computes expected values by re-implementing the production logic in the test.

**Tests the wrong thing**
- Asserts on implementation details, such as private methods, call order, or call counts, instead of observable behavior.
- The test name promises behavior the body does not check.
- Duplicates another test without adding a new case.

**Unreliable**
- Uses fixed sleeps, depends on the real clock or timezone, or uses random data without a seed.
- Depends on test order or on state left by another test.
- Is skipped, disabled, focused with `.only`, or marked expected-to-fail without a reason.

## Report format

```markdown
## Test audit: <PR title or branch>

**Verdict:** <one sentence: would these tests catch a broken version of this change?>

Target: <head commit> against <base commit>. Execution: <tests run, or static audit only>.
Assumed mockable: <services>. Real stack available: <what the test setup provides>.

### Findings
1. **<severity>** `<path>:<line>` `<test name>`
   <What is wrong, in plain words, and why it matters.>
   Fix: <the concrete change, for example "use the `db` fixture and assert the row exists instead of mocking `UserRepo.save`">.
   <If mutation-checked: the exact mutation, baseline and mutated test results, and whether execution of the mutated code was verified. Label inconclusive checks explicitly.>

### Missing tests
- <behavior from the change that no test covers, and where a test should go>

### Fine
<Tests that hold up, in one or two lines, so the user knows they were checked.>
```

Use three severities. **High** means the test would pass with the feature broken. **Medium** means the test covers the feature only partly, or only through mocks of the project's own code. **Low** covers style, reliability, and duplication.

Order findings by severity. Skip categories with nothing to report. After the report, offer to fix the findings.
