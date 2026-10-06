# Software Development Fundamentals (SDF05): Midterm Answers

**Universitas Cakrawala**

| Name | NIM |
| :--- | :--- |
| Muhammad Azhar Khaira | 25120300010 |

All answers are in this README. The code for C1 and D1 is in [`answers.py`](answers.py) and can be run directly:

```bash
python3 answers.py              # prints the C1 and D1 demonstrations, then runs the tests
python3 -m pytest answers.py    # optional, same tests through pytest
```

---

## Section A: Multiple Choice

| No | Answer | Reason |
| :-- | :--: | :--- |
| A1 | **c** | Professional code is code that other people can read, test and change safely. The other options measure activity or tools. |
| A2 | **b** | `calculate_order_total` is a verb phrase that states the result. `proc`, `doStuff` and `calc2` say nothing, and option d is too long and leaks details. |
| A3 | **d** | Refactoring changes internal structure while the intended behavior stays the same. |
| A4 | **a** | The same discount rule written three times must be changed in three places, which is the duplicated-code smell. |
| A5 | **c** | Modules group related code (high cohesion) and depend on each other as little as possible (low coupling). |
| A6 | **b** | The staging area (index) holds the changes chosen for the next commit. |
| A7 | **d** | `<<<<<<< HEAD` opens the part that comes from the current branch, the one checked out when `git merge` ran. |
| A8 | **c** | It follows Conventional Commits and says exactly what changed. |
| A9 | **a** | Purpose, summary and test evidence are what a reviewer needs to judge a change. |
| A10 | **b** | An unexplained behavior change without a test is a correctness risk, so it blocks the merge. |

---

## Section B: Short-Answer Questions

### B1. Refactoring and feature changes

Refactoring changes the internal structure of code (names, function boundaries, modules) while the observable behavior stays the same.
A feature change deliberately changes or adds behavior, so the output for some input becomes different.
For refactoring, existing tests are the proof that nothing changed. They must stay green without being edited.
For a feature change, new tests define the new expected behavior and old tests catch regressions in everything else.
Keeping the two in separate commits makes it clear which kind of change caused a failing test.

### B2. Git states

The working tree is the set of files on disk that are being edited. Changes there are not recorded yet.
The staging area (index) is a snapshot of the changes selected for the next commit.
A commit is a permanent snapshot in the repository history with a hash, author, message and parent.
Commands: `git add <file>` moves changes from the working tree to the staging area and `git commit -m "..."` turns the staged snapshot into a commit.
`git status`, `git diff` and `git diff --staged` show what is in each state before moving on.

### B3. Merge conflicts

A conflict happens when two branches change the same lines of a file (or one edits a file the other deletes) since their common ancestor, so Git cannot choose automatically.
Steps: (1) run `git merge <branch>` and Git reports `CONFLICT` and stops; (2) run `git status` to list the files under "both modified";
(3) open each file, combine the two versions between `<<<<<<<`, `=======` and `>>>>>>>`, then delete the markers;
(4) run the tests, then `git add <file>` to mark it resolved; (5) run `git commit` to create the merge commit.
`git merge --abort` cancels the merge at any point before the commit.

### B4. Code review

Three aspects to check: correctness (does the code do what the change claims, including edge cases), design (structure, cohesion, coupling, fit with the existing architecture) and tests (are the new behaviors and risky paths covered).
Style comes last because a wrong behavior or a poor design can force the code to be rewritten, and then every style comment is wasted.
A long list of style nits also hides the blocking issues and gives a false sense that the change was reviewed properly.
Most style rules can be enforced automatically by a formatter or linter, so human attention is better spent on behavior and design.

### B5. Cohesion and coupling

Cohesion is how closely the contents of one module serve a single responsibility (high is good).
Coupling is how much one module depends on the internals of other modules (low is good).
Example: in a single `app.py`, the discount and tax rules sit between CSV reading and printing code.
Moving them into a separate `pricing.py` with pure functions and no imports makes that module about pricing only, so cohesion rises.
`pricing.py` depends on nothing and callers use only its public functions, so coupling does not grow.

---

## Section C: Practical Section

### C1. Refactoring (12 points)

```python
def p(x, y, f):
    t = x * y
    if f:
        t = t * 0.9
    return t * 1.11
```

#### a. Code-quality problems

1. **Meaningless names.** `p`, `x`, `y`, `f` and `t` hide the intent. A reader has to work out that `x` is a unit price, `y` a quantity and `f` the member flag.
2. **Magic numbers.** `0.9` (10% member discount) and `1.11` (11% tax) have no name. Changing the tax rate means searching the codebase for `1.11`.
3. **Several responsibilities in one function.** Subtotal, discount and tax are mixed, so each step cannot be tested or reused on its own.
4. **Unclear boolean flag.** A call such as `p(100, 2, True)` does not say what `True` means.
5. **One variable with changing meaning.** `t` is first the subtotal, then the discounted amount.
6. **No documentation and no type hints.** Money is also stored as `float`, which produces values like `199800.00000000003`. This is noted but not changed, since a refactoring must not change results.

#### b. Refactored version

From [`answers.py`](answers.py):

```python
# factors keep the exact float literals of the legacy code so results stay bit-identical
MEMBER_DISCOUNT_FACTOR = 0.9  # members pay 90% of the subtotal (10% discount)
TAX_FACTOR = 1.11  # 11% VAT added on top of the discounted amount

def calculate_subtotal(unit_price: float, quantity: int) -> float:
    return unit_price * quantity

def apply_member_discount(amount: float, is_member: bool) -> float:
    if is_member:
        return amount * MEMBER_DISCOUNT_FACTOR
    return amount

def apply_tax(amount: float) -> float:
    return amount * TAX_FACTOR

def calculate_order_total(unit_price: float, quantity: int, is_member: bool) -> float:
    '''Total price after the member discount (if any) and tax.'''
    subtotal = calculate_subtotal(unit_price, quantity)
    discounted = apply_member_discount(subtotal, is_member)
    return apply_tax(discounted)
```

Each function has one job, the rates have names and a call site can read
`calculate_order_total(100_000, 2, is_member=True)`.

#### c. Why the behavior is preserved

The refactored code performs the same three multiplications, in the same order, with the same float values
(`0.9` and `1.11` are stored as constants, not recomputed). `if is_member:` treats truthy and falsy values exactly like
`if f:`. No validation, rounding or new rule was added, so only names and structure changed.

Example with `x = 100000`, `y = 2`, `f = True`:

| Step | Legacy `p` | Refactored |
| :--- | :--- | :--- |
| Subtotal | `t = 100000 * 2 = 200000` | `calculate_subtotal(100000, 2) = 200000` |
| Member discount | `t = 200000 * 0.9 = 180000.0` | `apply_member_discount(200000, True) = 180000.0` |
| Tax | `180000.0 * 1.11` | `apply_tax(180000.0)` |
| Result | `199800.00000000003` | `199800.00000000003` |

Both versions return the same float, including the rounding noise. `test_refactor_matches_legacy_exactly` in
`answers.py` compares the two with `==` for 48 combinations of price, quantity and member flag.

#### d. One test to add

Input `unit_price=50_000`, `quantity=3`, `is_member=False`. Expected output `166_500` (150,000 plus 11% tax, no discount).
This test checks that the discount is never applied to non-members.

```python
def test_non_member_pays_subtotal_plus_tax():
    assert math.isclose(calculate_order_total(50_000, 3, False), 166_500)
```

### C2. Git (12 points)

The outputs quoted below come from running these commands in a test repository (commit hashes differ on every run).

#### a. Branch, change, commit, return to `main`

```bash
git switch -c feat/member-discount       # same as: git checkout -b feat/member-discount
# edit pricing.py (and its test in tests/test_pricing.py)
git status
git diff
python3 -m pytest
git add pricing.py tests/test_pricing.py
git commit -m "feat: add member discount"
git switch main                           # same as: git checkout main
```

#### b. Merge into `main`

```bash
git merge feat/member-discount
```

**Fast-forward.** If `main` has no new commit since the branch was created, `main` is simply behind the branch.
Git moves the `main` pointer forward to the branch tip, no merge commit is created and the history stays linear:

```
Updating ce41c78..b7c958a
Fast-forward
 pricing.py | 5 ++++-
```

**Conflict.** If `main` also got a commit that changed the same lines of `pricing.py` (for example the tax rate
changed from 11% to 12%), Git cannot combine the two versions. It writes conflict markers into the file, stops the
merge and waits:

```
Auto-merging pricing.py
CONFLICT (content): Merge conflict in pricing.py
Automatic merge failed; fix conflicts and then commit the result.
```

(When both branches have new commits but touch different lines, Git creates a merge commit automatically.)

#### c. `git status` during a conflict, and the three steps to resolve it

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   pricing.py
```

Git says the merge is still in progress, lists `pricing.py` under *Unmerged paths* as *both modified* and
gives hints for finishing or aborting. The file itself contains both versions:

```
<<<<<<< HEAD
    return unit_price * quantity * 1.12
=======
    subtotal = unit_price * quantity
    if is_member:
        subtotal = subtotal * 0.9
    return subtotal * 1.11
>>>>>>> feat/member-discount
```

1. **Edit the file.** Combine the correct parts of both sides (here the member discount from the branch and the 12% tax
   from `main`) and remove every marker. Then run the tests.
2. **Mark it resolved** with `git add pricing.py`.
3. **Finish the merge** with `git commit`, which creates the merge commit with two parents.

#### d. Cancelling an unfinished merge

```bash
git merge --abort
```

It stops the merge and tries to restore the state from before `git merge` was run. `HEAD`, the staging area and the
working tree go back to the last commit of `main`, the conflict markers disappear and `git status` reports
`nothing to commit, working tree clean`. The feature branch is not touched, so the merge can be tried again later.
If there were uncommitted changes when the merge started, Git may not be able to restore them, which is why a merge
should start from a clean working tree, as in this question.

### C3. Modularization (11 points)

#### a. Module breakdown

| Module | Responsibility |
| :--- | :--- |
| `models.py` | Data classes such as `OrderLine` and `ReportData`. No logic, no I/O. |
| `pricing.py` | Business rules: subtotal, discount, tax (the functions from C1). |
| `calculator.py` | Prices each order line and computes the grand total, using `pricing.py`. |
| `reader.py` | Turns CSV text from any text stream into `OrderLine` objects (parsing and type conversion). |
| `report.py` | Builds the text of `report.txt` and the console summary. Returns strings and prints nothing. |
| `file_io.py` | Opens `orders.csv` and writes `report.txt`. The only module that touches the file system. |
| `app.py` | Entry point: wires the modules together, chooses file names and prints the summary. |

#### b. Dependency direction

```
app.py ──► file_io ──► reader ──► models
   │                               ▲
   ├──► calculator ──► pricing     │
   │         └─────────────────────┤
   └──► report ────────────────────┘
```

Dependencies point from the outer layer (entry point and file I/O) toward the core (business rules and data).
`pricing.py` and `models.py` import nothing from the project. The reasons:

- Business rules change for business reasons (a new tax rate) while input and output change for technical reasons (a new
  file format). With this direction, a change in the CSV format touches only `reader.py`, and a new tax rate touches only `pricing.py`.
- The core can be reused by a different entry point, such as a web API or a JSON input, without dragging file code along.
- There are no import cycles.

#### c. Modules that can be tested without the file system

`pricing.py`, `models.py`, `calculator.py`, `report.py` and `reader.py`. The reader accepts any text stream, so a test can
pass it an `io.StringIO` instead of a real file, and the report module returns a string instead of writing one.
Only `file_io.py` and `app.py` need real files, and one test with a temporary folder is enough for them.

This matters because in-memory tests are fast and deterministic. They leave no files behind and do not depend on the
working directory or file permissions. Edge cases such as an empty order list are one line of data, and a failing test
points at the logic, not at the environment.

#### d. Two risks of splitting the code without testing first

1. **Silent behavior change.** A small slip while moving code, such as applying tax before the discount, changing how
   the member column is parsed (`"yes"` vs `"Yes"`) or rounding at a different step, changes the numbers in the report.
   Without a test that captured the old output, nobody notices until a customer or the finance team does.
2. **Broken wiring and output.** Wrong imports, an import cycle, a wrong file path or a shifted column in `report.txt`
   only show up when that path is executed. The program may still run, so the error stays hidden.

Both risks are reduced by writing a golden master test before splitting: run the old `app.py` on a fixed `orders.csv`,
save `report.txt` and the console output, and assert that the new modules produce exactly the same text.

---

## Section D: Code Review Case Study

### D1

```diff
 def calculate_average(scores):
-    return sum(scores) / len(scores)
+    d = scores
+    total = 0
+    for i in range(len(d)):
+        total = total + d[i]
+    return total / len(d) + 1
```

In `answers.py` the two versions are `calculate_average_before` and `calculate_average_pr`.

#### a. Problems and classification

| # | Problem | Class | Why this class |
| :-- | :--- | :--- | :--- |
| 1 | `+ 1` is added to the result. Every average is now 1 higher than the true mean. | **Blocking** | It is a correctness bug that changes the output for every caller. |
| 2 | No test is added for a change that alters behavior. | **Blocking** | The change cannot be verified, and the existing behavior is not protected against regression. |
| 3 | The description "small improvement to the average function" does not mention that the output changes. | **Blocking** | It hides a behavior change. Without the purpose, a reviewer cannot tell whether `+ 1` is intended. |
| 4 | The manual loop replaces `sum()`. For a normal list it gives the same total but needs four lines instead of one and runs slower. | **Suggestion** | The result is correct, so it does not block, but it makes the code worse and adds places for bugs. |
| 5 | `d = scores` adds a one-letter alias with no meaning. | **Nit** | Readability only, no effect on behavior. |
| 6 | `for i in range(len(d))` with `d[i]` instead of `for score in scores`, and `total = total + ...` instead of `+=`. | **Nit** | Style that is not idiomatic Python. Behavior is the same. |
| 7 | An empty list still raises `ZeroDivisionError`. | **Suggestion** | The problem already existed before the PR, so it should be a separate issue or PR rather than a reason to block this one. |

#### b. Three review comments

**Comment 1, line `return total / len(d) + 1` (blocking)**
- *Problem:* `+ 1` is added to the mean and the PR does not explain why.
- *Impact:* every caller now gets a value 1 higher than the real average. For `[2, 4, 6]` the result becomes `5.0` instead of `4.0`, which affects grades, reports and anything built on this function.
- *Proposed improvement:* remove `+ 1`. If an offset is really required, put it in a separately named function (for example `calculate_adjusted_average`) with the business reason in the PR description and a test for it.

**Comment 2, the PR as a whole (blocking)**
- *Problem:* the PR changes the output of the function but adds no test and describes itself as a "small improvement".
- *Impact:* the change cannot be verified, the wrong `+ 1` is not caught and later changes have no safety net.
- *Proposed improvement:* add `test_average_of_2_4_6_is_4` (see d) and update the description with the purpose of the change, a summary and the test results.

**Comment 3, the loop (suggestion)**
- *Problem:* the manual loop with `d`, `i` and `d[i]` replaces a one-line `sum(scores)`.
- *Impact:* the code becomes longer and harder to read with no gain. The built-in `sum` is faster and has already been tested.
- *Proposed improvement:* keep `return sum(scores) / len(scores)`. If the goal was readability, the original line already reads well.

#### c. Behavior change for `scores = [2, 4, 6]`

| Version | Calculation | Result |
| :--- | :--- | :--- |
| Before | `sum([2, 4, 6]) / len([2, 4, 6]) = 12 / 3` | `4.0` |
| After | `total = 2 + 4 + 6 = 12`, then `12 / 3 + 1` | `5.0` |

Division is evaluated before addition, so the PR computes `(12 / 3) + 1`, not `(12 + 1) / 3`.
The mean of `[2, 4, 6]` is 4, so the new result is wrong by exactly 1.

#### d. Test to request from the author

```python
def test_average_of_2_4_6_is_4():
    assert calculate_average([2, 4, 6]) == 4
```

This test fixes the expected behavior with a case that can be checked by hand. It passes on the original version and
fails on the PR version, so it catches the `+ 1` right away and prevents the same change from slipping in later.
`python3 answers.py` shows this: the same check on the PR version prints `False`.

#### e. Empty list

| Version | What happens with `[]` |
| :--- | :--- |
| Before | `sum([])` is `0` and `len([])` is `0`, so `0 / 0` raises `ZeroDivisionError: division by zero`. |
| After | The loop never runs, `total` stays `0`, and `0 / 0` raises `ZeroDivisionError` before `+ 1` is reached. |

Both versions crash with an error that does not explain the cause. The average of no scores is undefined, so the
function should reject the input explicitly instead of returning a made-up value such as `0`, which cannot be told apart
from a real average of 0. Recommended version in `answers.py`:

```python
def calculate_average(scores):
    '''Arithmetic mean of scores, raises ValueError for an empty list.'''
    if not scores:
        raise ValueError("scores must not be empty")
    return sum(scores) / len(scores)
```

It is covered by `test_empty_list_raises_value_error`. Changing the error type from `ZeroDivisionError` to `ValueError`
is itself a behavior change, so it belongs in its own PR with this test and a clear description.