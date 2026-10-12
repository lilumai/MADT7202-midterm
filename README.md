# MADT 7202 Mid-Term — Geely or MG first? Two EV deals, mostly different shoppers

Evidence repository for the one-page report (`MADT7202_Midterm.pdf`). Every number in the report is printed by one of the scripts below.

## Question
Each month a Thai bank's Head of Pricing & Strategy (auto finance) spends a fixed rate-subsidy budget on car-maker deals. Does any car model link otherwise separate shopper groups, and do Geely and MG draw on the same shoppers?

## Data (what is and is not in this repo)
| Source | How | In repo? |
|---|---|---|
| YouTube Data API v3 — 817 videos, 23,291 top-level comments, 1 Jan–11 Oct 2026 | `youtube_collect.py` (batch 1, 4 generic queries) + `youtube_collect2.py` (batch 2, 6 generic queries, no shared video) | **No raw comment text** (stays offline). Only derived ids + model names: `data/processed/comment_models_v2.csv` |
| Pantip car room — 7 thread titles naming two models | **Collected by hand** through the site's own search ("ลังเลระหว่าง", "เลือกระหว่าง"); Pantip blocks bots, so no script touched Pantip for collection | `data/raw/pantip_manual.csv` (topic id, date, the two models; no usernames) |

No model name was used as a search term. No author or channel names were stored. API keys are read from the `YOUTUBE_API_KEY` environment variable and are not in any file.

## Pipeline (run in this order, from the repo folder)
| Step | Script | Prints / writes | Used in report |
|---|---|---|---|
| 1 | `youtube_collect.py`, `youtube_collect2.py` | raw data (not committed) | 3 Data |
| 2 | `extract_candidates.py` | window check, name candidates | 3 Data (period, volume) |
| 3 | `count_models_v2.py` | model mentions; ORA 5 split EV/HEV; `comment_models_v2.csv` | 3 Data (237 comments), 4 Filtering |
| 4 | `build_graph_v2.py` | 23 nodes / 26 links / 3 pieces; inside share; betweenness; 40-run robustness grid; `graph_edges_baseline_v2.csv` | 4 Result & Alternatives, 6 Findings |
| 5 | `cross_fuel_check.py` | fuel-crossing links at 1/2/3 videos; Geely→MG paths | 6 Finding 1–2 |
| 6 | `batch_replication.py` | batch 1 vs batch 2 replication | 3 Corroboration, 6 Finding 1 |
| 7 | `pantip_check.py` | Pantip counts; models missing from the alias list | 3 Data, 6 Findings, 8 |
| 8 | `inspect_edges.py` | comments behind chosen pairs (hand audit, read locally) | 4 Filtering, 6 Finding 3, 8 |
| 9 | `make_figure.py` | `figure_baseline.png` | 5 The picture |

Earlier versions kept for transparency: `count_models.py` and `build_graph.py` (before the edge audit), `pantip_probe.py` (structure probe; Pantip was then excluded from automated collection).

## Decisions fixed before results
Edge = two models in the same comment; keep a pair only if seen under ≥3 different videos; groups = size (B or smaller / C+) × fuel (ICE incl. HEV/PHEV/REEV / BEV); gate: inside share ≥ 0.80 and one piece without the top-betweenness node = no bridge.
Changed **after** the hand audit (disclosed in the report): ORA 5 split into EV and HEV; added the choice-word and ≤3-models-per-comment variants.

## Requirements
`pip install -r requirements.txt` (Python 3.9+). Week 6–8 methods only: co-mention graph, NPMI, degree, betweenness, connected pieces, inside share.

Note on pantip_probe.py: it sent 3 page requests to Pantip on 11 Oct 2026 (a search page, a room page, one thread page) to check how the pages are built, before Pantip's bot-block notice was seen. Nothing from it is used in the report. All Pantip data in the report was collected by hand.
