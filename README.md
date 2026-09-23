# FastBox — Mystery Delivery System

Python assignment for Nexgensis.
 Built a small logistics simulator -: Basically packages get assigned to the nearest agent, agents
"deliver" them, and at the end I get a report on who did the most work and how
efficiently.

Wrote this to actually be correct on messy/different input formats, not just
the one example file. More on that below because it ended up being the whole
point of the assignment imo.

## Structure

```
fastbox_delivery/
├── data.json                  # the example input from the PDF
├── report.json                # report.json generated from data.json
├── report_top_performer.csv   # bonus: csv of the top agent
├── src/
│   ├── models.py               # Warehouse / Agent / Package classes
│   ├── data_loader.py          # reads + parses the JSON (task 1)
│   ├── distance.py             # euclidean distance, one function
│   ├── assignment.py           # nearest-agent assignment logic (task 3a)
│   ├── simulator.py            # actually simulates the deliveries (task 3b)
│   ├── report.py               # builds report.json + the csv bonus
│   ├── visualizer.py           # ascii map bonus
│   ├── bonus_features.py       # new agent joining mid-day bonus
│   └── main.py                 # runs everything, has the CLI flags
├── tests/
│   └── test_simulator.py       # unit tests, run against all 11 test cases
└── test_cases/                 # all the test case files provided
```

## Running it

```bash
cd src
python main.py ../data.json                   # basic run, writes report.json
python main.py ../data.json --csv --ascii      # also dumps a csv + ascii map
python main.py ../test_cases/base_case.json    # works on the other json format too
python main.py ../data.json --demo-new-agent   # shows the mid-day agent bonus
python main.py --help                          # see all flags
```

Tests (run from project root):
```bash
python -m unittest tests.test_simulator -v
```

No installs needed, no requirements.txt — everything's stdlib (`json`, `math`,
`random`, `csv`, `argparse`).

## Example output

Running `python main.py ../data.json --csv --ascii` on the sample data:

```
=== DELIVERY REPORT ===
  A1: delivered=2   distance=121.21   efficiency=60.61
  A2: delivered=2   distance=79.21    efficiency=39.6
  A3: delivered=1   distance=14.14    efficiency=14.14
  Best agent: A3

Saved report to: report.json
Saved top performer CSV to: report_top_performer.csv

=== ASCII MAP (final agent positions) ===
+------------------------------------------------------------+
|                      2                                     |
|                            W                                |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                        W    |
|                                                           3 |
|                                                              |
|                                                              |
|     1                                                       |
|                                                              |
|                                                              |
|W                                                             |
+------------------------------------------------------------+
Legend: W = warehouse | digit = agent's final position (e.g. '1' = A1)
```

W's are the warehouses, and the numbers are where each agent ended up after
finishing their route. Genuinely just for a quick sanity check that the
positions look right without needing to load up matplotlib for something
this simple.

## How I approached it

Pretty much followed the brief task by task, one file per task basically:

1. Parse the JSON manually —: no pandas or anything, just `json.load`.
2. For each package, find whichever agent starts closest to that package's
   warehouse and assign it there.
3. Simulate the day —: each agent works through their assigned packages,
   picking up and dropping off, and I track the distance as they go.
4. Build the report —: packages delivered, distance, efficiency per agent, and
   who the best one was.
5. Then the bonus stuff: random delays, an ascii map so you can actually see
   the layout without matplotlib, handling a new agent showing up mid-day, and
   a csv export.

## The thing I actually want to call out

The brief gives you one example `data.json`, but the test case files given
separately don't all follow that same structure. `base_case.json` for example
writes warehouses/agents as a list of objects (`[{"id": "W1", "location":
[x,y]}]`) instead of a dict (`{"W1": [x,y]}`), and calls the package's
warehouse field `warehouse_id` instead of `warehouse`.

What's kind of funny is `base_case.json`'s actual numbers are identical to the
PDF's `data.json` example, just written in the other format , so this
definitely wasn't an accident on their end. Given the brief literally says
"test your code with different JSON inputs," I'm pretty confident this was
put there on purpose to see if people's parsers would break on it. A bunch of
people are probably going to hardcode one shape and fail half the hidden test
cases without realizing why.

So `data_loader.py` detects which format it's looking at and normalizes both
into the same internal objects before anything else touches the data. Ran it
against all 11 provided test files (base case + test_case_1 through 10) and
it parses every one without any special-casing per file.

## Assumptions I made (and why)

The assignment says to make a reasonable call on anything ambiguous and document
it instead of stopping to ask , so here's everything I had to decide on my own,
same order they show up in the code:

**1. Which agent position counts for assignment —: start or current?**
I used each agent's starting position, not something that updates mid-way.
If it updated as you assign packages, the result would depend on which order
you happened to loop through the packages in, which felt wrong , assigning
should be a one-time planning step before anyone actually moves.

**2. Ties in distance.**
If two agents are exactly the same distance from a warehouse (rare, but
possible), I just go with whichever agent ID sorts first (A1 before A2 etc).
Doesn't really matter which rule you pick here, it just needs to be
consistent so results don't randomly change between runs.

**3. What order does an agent do its packages in?**
Not specified at all in the brief. Doing them in whatever order they appear
in the input would give a genuinely worse, unrealistic distance. So instead
each agent always goes to whichever of its remaining packages has the closest
warehouse from wherever it currently is (basically nearest-neighbor). It's
not a perfect TSP solve, but it's the obvious sane approach and way more
realistic than random ordering.

**4. Random delays (bonus).**
These only affect a separate `delay` field on the package, they don't touch
`total_distance` , didn't want randomness messing with the actual graded
numbers. Seed is fixed at 42 by default so it's reproducible, but you can
override it with `--seed`.

**5. What "efficiency" means.**
The sample report in the assignment  has `total_distance / packages_delivered =
efficiency` (85.32 / 2 = 42.66 checks out exactly), so that's the definition
I went with — basically average distance per delivery, lower = better.
`best_agent` = whoever has the lowest efficiency out of the agents that
actually delivered something.

**6. Agents that get zero packages.**
Happens more than you'd think depending on the geometry of a test case (a
couple of the provided ones have 2-3 agents get nothing at all). Rather than
crashing on a divide by zero, I just report `efficiency: 0.0` for them and
don't let them be picked as `best_agent`.

**7. "New agent joins mid-day" (bonus).**
There's no actual clock in this simulation so "mid-day" doesn't mean anything
on its own. I treated it as: some packages are already delivered, some
aren't yet, and a new agent shows up right at that point. Only the
undelivered packages get pooled up and re-assigned across everyone (old
agents + the new one), using the same nearest-warehouse logic as before —
except agents already mid-route get compared from where they currently are,
not their original start point, since they've obviously moved by then.
Anything already delivered stays untouched.

## Testing

`tests/test_simulator.py` runs the full pipeline against all 11 provided
test files and checks:
- total delivered packages == total packages (this is literally called out
  in the brief as something to double check)
- every package actually gets marked delivered
- no negative distances anywhere
- `best_agent` is always set when at least one delivery happened
- efficiency in the report actually matches distance/delivered

All of it passes on every test case, including the ones where some agents
end up with zero deliveries.

Thank you :)
