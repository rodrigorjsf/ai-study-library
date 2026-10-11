# Update branch

The file exists, so it is the starting point: the result is a minimal diff against it, not a rewrite. Human-written rules carry intent the code cannot show, so a rule stays unless the evidence removes it.

## In step 5: give every existing rule a verdict

Parse the existing file into individual rules and check each against the codebase as it is now.

| Verdict | Test | Action |
|---|---|---|
| **holds** | the code still follows it | keep its wording untouched; refresh the exemplar if the path moved |
| **drift** | recent code consistently does something else | a step 6 question: is the rule wrong, or the code? |
| **enforced** | a config in the enforced set now checks it | remove; the domain section names the config |
| **restated** | a project rule file states the same meaning | keep it here; step 9 removes it from the rule file |
| **user-level** | it copies a user-level rule | replace the copy with a pointer to the rule file |
| **duplicate** | the same meaning appears twice in this file | keep one |
| **unverifiable** | no site in the codebase exercises it | keep, and list it for the user as unverified |
| **no-op** | a reviewer applies it by default | propose removal |

Check every existing pointer too, both `_Detail:_` and user-level: a pointer whose path is gone is removed, one whose subject changed gets its line refreshed, and a `_Detail:_` target that is no longer on demand is switched back in step 9.

Also diff the domains: a domain heading whose code is gone is removed, and a present domain with no heading is added.

Done when every existing rule carries exactly one verdict.

## In step 7: preserve what holds

Keep the existing heading order, heading names, and rule wording wherever the verdict is **holds**. Add new rules under their domain heading in the step 7 shape. If the existing file uses a different rule shape consistently, follow the file's shape.

## In step 8: show a change list

Before the draft, give the user a table with one row per changed rule: domain, rule name, verdict or `new`, and the evidence (`N of M`, exemplar). Rules with verdict **holds** are counted in one summary line, not listed.

Done when every existing rule is accounted for in the table or the summary count, and the two sum to the number of rules parsed.
