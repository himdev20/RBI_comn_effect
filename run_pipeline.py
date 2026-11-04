"""Stage runner. Run stages in this order the first time (see docs/RUNBOOK.md):

  python run_pipeline.py market          # downloads/ + series_map.csv -> raw/market/yields.csv
  python run_pipeline.py scrape          # optional: fetch minutes listed in minutes_urls.csv
  python run_pipeline.py parse [--debug] # minutes -> member_statements.csv, meeting_texts.csv
  python run_pipeline.py check           # validate every input; fix FAILs before going on
  python run_pipeline.py score [--llm] [--vader] [--finbert] [--limit=10]
  python run_pipeline.py validate-draw   # sample for hand-coding (then code it, see CODEBOOK)
  python run_pipeline.py validate        # human vs machine agreement
  python run_pipeline.py shocks          # decision-day surprise series (text-free)
  python run_pipeline.py build           # merge everything
  python run_pipeline.py analyze [--B=2000]   # decision_day, event_study, linkage, predictability
  python run_pipeline.py figures
  python run_pipeline.py report          # outputs/summary.md
  python run_pipeline.py all [--llm]     # parse -> report in one go (after market + scoring)

Environment variables: RBI_SCORE (hawk_llm|hawk_dict), RBI_SURPRISE (gov|res|roll),
RBI_LLM_MODEL (pinned model id), ANTHROPIC_API_KEY, RBI_DROP_UNSCHEDULED=1,
RBI_ALLOW_UNVERIFIED=1 (dry runs only).
"""
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(), logging.FileHandler(Path(__file__).parent / "pipeline.log")])
from src import config  # noqa: E402

args = sys.argv[1:]
stage = args[0] if args else "help"
B = next((int(a.split("=")[1]) for a in args if a.startswith("--B=")), 2000)


def score():
    from src import score_dictionary
    score_dictionary.run()
    if "--vader" in args:
        from src import score_vader; score_vader.run()
    if "--finbert" in args:
        from src import score_finbert; score_finbert.run()
    if "--llm" in args:
        from src import score_llm
        lim = next((int(a.split("=")[1]) for a in args if a.startswith("--limit=")), None)
        score_llm.run(limit=lim)


def analyze():
    from src import decision_day, event_study, linkage, predictability
    if (config.PROC / "shocks.csv").exists():
        decision_day.run()
    event_study.run(B=B)
    linkage.run(B=B)
    predictability.run()


STAGES = {
    "market": lambda: __import__("src.assemble_market", fromlist=["run"]).run(),
    "scrape": lambda: __import__("src.scrape_minutes", fromlist=["run"]).run(),
    "parse": lambda: __import__("src.parse_minutes", fromlist=["run"]).run(debug="--debug" in args),
    "check": lambda: sys.exit(0 if __import__("src.check_data", fromlist=["run"]).run() else 1),
    "score": score,
    "validate-draw": lambda: __import__("src.validate", fromlist=["draw_sample"]).draw_sample(),
    "validate": lambda: print(__import__("src.validate", fromlist=["evaluate"]).evaluate().round(3).to_string()),
    "shocks": lambda: __import__("src.shocks", fromlist=["run"]).run(),
    "build": lambda: __import__("src.build_dataset", fromlist=["run"]).run(),
    "analyze": analyze,
    "figures": lambda: __import__("src.figures", fromlist=["run"]).run(),
    "report": lambda: __import__("src.report", fromlist=["run"]).run(),
}

if stage == "all":
    from src import check_data
    for s in ["parse"]:
        STAGES[s]()
    if not check_data.run():
        sys.exit("data check failed - see outputs/tables/data_check.md")
    score()
    for s in ["shocks", "build", "analyze", "figures", "report"]:
        logging.info("== %s", s); STAGES[s]()
elif stage in STAGES:
    STAGES[stage]()
else:
    print(__doc__)
