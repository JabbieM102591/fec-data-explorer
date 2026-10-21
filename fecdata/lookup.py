import pandas as pd

SIZE_LABELS = {
    0: "$200 and under",
    200: "$200.01 - $499.99",
    500: "$500 - $999.99",
    1000: "$1,000 - $1,999.99",
    2000: "$2,000 and over",
}

# Donors type these in the employer box when they have no employer to report.
PLACEHOLDER_EMPLOYERS = {
    "NOT EMPLOYED", "SELF-EMPLOYED", "SELF EMPLOYED", "SELF", "RETIRED", "NONE",
    "N/A", "NA", "UNEMPLOYED", "HOMEMAKER", "REQUESTED", "INFORMATION REQUESTED",
    "INFO REQUESTED", "INFORMATION REQUESTED PER BEST EFFORTS",
}


def search_candidates(client, name, max_results=10):
    return client.get("candidates/search", q=name, per_page=max_results).get("results", [])


def principal_committee_id(candidate):
    for c in candidate.get("principal_committees") or []:
        if c.get("committee_id"):
            return c["committee_id"]
    return None


def _frame(rows, columns):
    df = pd.DataFrame(rows)
    for col in columns:
        if col not in df.columns:
            df[col] = None
    return df[columns].copy()


def _small_share(totals):
    small = totals.get("individual_unitemized_contributions") or 0
    large = totals.get("individual_itemized_contributions") or 0
    return small / (small + large) if (small + large) > 0 else 0


def small_donor_share_for(client, candidate_id, cycle=2024):
    """Small-donor share for one candidate, from the single-candidate totals record."""
    results = client.get(f"candidate/{candidate_id}/totals", cycle=cycle).get("results") or [{}]
    return _small_share(results[0])


def size_breakdown(rows):
    df = _frame(rows, ["size", "total", "count"])
    for col in ["size", "total", "count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["total"] = df["total"].fillna(0)
    df["count"] = df["count"].fillna(0)
    df["bucket"] = df["size"].map(SIZE_LABELS)
    return df.sort_values("size").reset_index(drop=True)


def clean_employers(df):
    """Drop placeholder employers such as NOT EMPLOYED so real employers show up."""
    if df.empty:
        return df
    name = df["employer"].fillna("").str.strip().str.upper()
    return df[~name.isin(PLACEHOLDER_EMPLOYERS) & (name != "")].reset_index(drop=True)


def candidate_profile(client, candidate, cycle=2024):
    cid = candidate["candidate_id"]
    results = client.get(f"candidate/{cid}/totals", cycle=cycle).get("results") or [{}]
    totals = results[0]
    committee_id = principal_committee_id(candidate)
    by_size, employers = pd.DataFrame(), pd.DataFrame()
    if committee_id:
        sizes = client.get("schedules/schedule_a/by_size", committee_id=committee_id,
                           cycle=cycle, per_page=20).get("results", [])
        by_size = size_breakdown(sizes)
        emp = client.get("schedules/schedule_a/by_employer", committee_id=committee_id,
                         cycle=cycle, sort="-total", per_page=50).get("results", [])
        employers = clean_employers(_frame(emp, ["employer", "total", "count"]))
    return {"totals": totals, "committee_id": committee_id,
            "small_donor_share": _small_share(totals),
            "by_size": by_size, "employers": employers}


def search_committees(client, name, max_results=10):
    return client.get("committees", q=name, per_page=max_results).get("results", [])


def contributions_to_df(rows):
    out = []
    for r in rows:
        rc = r.get("recipient_committee") or {}
        out.append({
            "recipient_name": r.get("recipient_name") or rc.get("name"),
            "recipient_party": rc.get("party") or "Unknown",
            "amount": r.get("disbursement_amount") or 0,
            "date": r.get("disbursement_date"),
        })
    df = pd.DataFrame(out, columns=["recipient_name", "recipient_party", "amount", "date"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    return df


def committee_contributions(client, committee_id, cycle=2024, max_pages=5):
    rows = client.keyset_paginate(
        "schedules/schedule_b", max_pages=max_pages, committee_id=committee_id,
        two_year_transaction_period=cycle,
        disbursement_purpose_category="CONTRIBUTIONS", per_page=100)
    return contributions_to_df(list(rows))


def summarize_recipients(df, n=10):
    g = df.groupby("recipient_name", dropna=True).agg(
        total=("amount", "sum"), gifts=("amount", "count")).reset_index()
    return g.sort_values("total", ascending=False).head(n).reset_index(drop=True)


def party_split(df):
    """Dollars by recipient party. Refunds (negative amounts) are left out."""
    gifts = df[df["amount"] > 0]
    g = gifts.groupby("recipient_party").agg(total=("amount", "sum"), gifts=("amount", "count"))
    g = g.reset_index().sort_values("total", ascending=False).reset_index(drop=True)
    whole = g["total"].sum()
    g["share"] = (g["total"] / whole).round(3) if whole else 0
    return g
