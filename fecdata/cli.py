import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

from . import lookup, stats
from .analysis import fetch_candidate_totals, summarize_by_party, top_n
from .client import FECClient


def _bar(labels, values, title, xlabel, path):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(list(labels)[::-1], list(values)[::-1])
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    fig.tight_layout()
    try:
        fig.savefig(path, dpi=150)
    except OSError as err:
        # Windows refuses to overwrite an image that is open in a viewer.
        print(f"Could not save chart {path} ({err}). Close it in any viewer and rerun.")
    finally:
        plt.close(fig)


def _outdir(args):
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    return out


def _show_stats(title, s, path):
    print(f"\n{title}")
    print(f"  n = {s['n']}, total = ${s['total']:,.0f}")
    print(f"  mean ${s['mean']:,.0f} vs median ${s['median']:,.0f} (ratio {s['mean_to_median']:.1f})")
    print(f"  median 95% CI: ${s['median_ci_low']:,.0f} to ${s['median_ci_high']:,.0f}")
    print(f"  HHI {s['hhi']:,.0f} (0 to 10,000), Gini {s['gini']:.3f}")
    if s["n"] < 10:
        print("  Note: fewer than 10 values, so these statistics are not reliable.")
    pd.DataFrame(list(s.items()), columns=["metric", "value"]).to_csv(path, index=False)


def cmd_totals(args):
    client = FECClient()
    df = fetch_candidate_totals(client, args.cycle, args.office, args.state, args.pages)
    if df.empty:
        print("No results. Try a different cycle, office or state.")
        return 1
    out = _outdir(args)
    tag = f"{args.office}_{args.state or 'US'}_{args.cycle}"
    df.to_csv(out / f"candidate_totals_{tag}.csv", index=False)
    summarize_by_party(df).to_csv(out / f"party_summary_{tag}.csv", index=False)

    top = top_n(df, args.top)
    shares = []
    for cid in top["candidate_id"]:
        try:
            shares.append(round(lookup.small_donor_share_for(client, cid, args.cycle), 3))
        except requests.RequestException:
            shares.append(float("nan"))
    top["small_donor_share"] = shares
    top.to_csv(out / f"top_fundraisers_{tag}.csv", index=False)
    print(top[["name", "party", "state", "receipts", "small_donor_share"]].to_string(index=False))

    _show_stats("Receipts across candidates", stats.summary(df["receipts"]),
                out / f"receipts_stats_{tag}.csv")
    _bar(top["name"], top["receipts"] / 1e6,
         f"Top fundraisers: {args.cycle} {args.office} {args.state or 'US'}",
         "Total receipts ($ millions)", out / f"top_receipts_{tag}.png")
    print(f"\nSaved files to {out}/")
    return 0


def cmd_candidate(args):
    client = FECClient()
    matches = lookup.search_candidates(client, args.name)
    if not matches:
        print("No candidates found.")
        return 1
    for i, m in enumerate(matches[:5], 1):
        print(f"{i}. {m['candidate_id']}  {m['name']}  {m.get('party')}  "
              f"{m.get('office')}-{m.get('state')}")
    cand = matches[min(args.pick, len(matches)) - 1]
    prof = lookup.candidate_profile(client, cand, args.cycle)
    t = prof["totals"]
    print(f"\n{cand['name']} ({args.cycle})")
    print(f"  Receipts:      ${t.get('receipts') or 0:,.0f}")
    print(f"  Disbursements: ${t.get('disbursements') or 0:,.0f}")
    print(f"  Cash on hand:  ${t.get('cash_on_hand_end_period') or 0:,.0f}")
    print(f"  Small-donor share of individual money: {prof['small_donor_share']:.1%}")
    out = _outdir(args)
    tag = cand["candidate_id"]
    if not prof["by_size"].empty:
        prof["by_size"].to_csv(out / f"{tag}_by_size.csv", index=False)
        print("\nIndividual contributions by size:")
        print(prof["by_size"][["bucket", "total", "count"]].to_string(index=False))
        _bar(prof["by_size"]["bucket"], prof["by_size"]["total"] / 1e6,
             f"{cand['name']}: contributions by size", "$ millions",
             out / f"{tag}_by_size.png")
    if not prof["employers"].empty:
        prof["employers"].to_csv(out / f"{tag}_top_employers.csv", index=False)
        print("\nTop donor employers (placeholders such as NOT EMPLOYED removed):")
        print(prof["employers"].head(5).to_string(index=False))
    print(f"\nSaved files to {out}/")
    return 0


def cmd_committee(args):
    client = FECClient()
    matches = lookup.search_committees(client, args.name)
    if not matches:
        print("No committees found.")
        return 1
    for i, m in enumerate(matches[:5], 1):
        print(f"{i}. {m['committee_id']}  {m['name']}  type={m.get('committee_type_full')}")
    com = matches[min(args.pick, len(matches)) - 1]
    df = lookup.committee_contributions(client, com["committee_id"], args.cycle, args.pages)
    if df.empty:
        print(f"\nNo itemized contributions found for {com['name']} in {args.cycle}.")
        return 1
    top = lookup.summarize_recipients(df, args.top)
    parties = lookup.party_split(df)
    print(f"\n{com['name']}: top recipients in {args.cycle}")
    print(top.to_string(index=False))
    print("\nGiving by recipient party (refunds left out):")
    print(parties.to_string(index=False))
    out = _outdir(args)
    tag = com["committee_id"]
    df.to_csv(out / f"{tag}_contributions.csv", index=False)
    parties.to_csv(out / f"{tag}_party_split.csv", index=False)
    _show_stats("Size of individual gifts", stats.summary(df["amount"]),
                out / f"{tag}_gift_stats.csv")

    gifts = df[df["amount"] > 0]
    if not gifts.empty:
        unknown = gifts.loc[gifts["recipient_party"] == "Unknown", "amount"].sum()
        print(f"  Recipients with no party on record: {unknown / gifts['amount'].sum():.1%} of dollars")
        known = gifts[gifts["recipient_party"] != "Unknown"]
        if not known.empty:
            party = known.groupby("recipient_party")["amount"].sum().idxmax()
            share, lo, hi = stats.bootstrap_share_ci(
                known["amount"], known["recipient_party"] == party)
            print(f"  Among recipients with a party, {party} got {share:.1%} "
                  f"(95% CI {lo:.1%} to {hi:.1%})")
    _bar(top["recipient_name"], top["total"] / 1e3,
         f"{com['name']}: top recipients", "$ thousands", out / f"{tag}_top_recipients.png")
    print(f"\nSaved files to {out}/")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="fecdata", description="Explore FEC money in politics.")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--cycle", type=int, default=2024, help="election year")
        sp.add_argument("--out", default="outputs")

    t = sub.add_parser("totals", help="top fundraisers for an office and state")
    common(t)
    t.add_argument("--office", choices=["H", "S", "P"], default="H")
    t.add_argument("--state", help="two-letter code such as DC, VA, MD")
    t.add_argument("--top", type=int, default=10)
    t.add_argument("--pages", type=int, default=3)
    t.set_defaults(func=cmd_totals)

    c = sub.add_parser("candidate", help="profile one candidate")
    common(c)
    c.add_argument("name")
    c.add_argument("--pick", type=int, default=1, help="which search match to use")
    c.set_defaults(func=cmd_candidate)

    m = sub.add_parser("committee", help="who a PAC or corporate committee gave to")
    common(m)
    m.add_argument("name")
    m.add_argument("--pick", type=int, default=1)
    m.add_argument("--top", type=int, default=10)
    m.add_argument("--pages", type=int, default=5)
    m.set_defaults(func=cmd_committee)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)
