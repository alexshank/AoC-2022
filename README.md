# AoC-2022

Advent of Code solutions for 2022 (mostly in Python). Fingers crossed we can learn some Haskell along the way.

---

## Structure

For each day, there will be the following files:

- `day-x-prompt.txt`
- `day-x-input.txt`
- `day-x.py`

---

## Selected Learnings

Thoughts, observations, and eurekas for each day.

#### Day 19
- Created an entire custom class which overloaded +, *, <=, etc. Could have just used a 4-Tuple, which already works intuitively.
- Main issue is reducing the problem space to a reasonable size. Heuristics are necessary, at least from what I can tell (no obvious, optimal solution that is fast).
- Needed to add profiling with this command: `python3 -m cProfile -s time day-19.py > day-19-profiler-results.txt`
    - Turns out tuples have been very inefficient.
    - Ultimately, pruning the search space was the only thing that made tangible improvements on execution time.
- Interestingly, the example input takes an indefinite amount of time to run for part 2. Ran it for ~10 mins before killing.
    - My solution worked for the actual challenge input though.
- I needed A LOT of hints and references from the Advent of Code Reddit threads. I would not have solved this without them.

---