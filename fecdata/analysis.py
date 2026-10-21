import pandas as pd

# The multi-candidate totals endpoint does not return unitemized contributions,
# so small-donor share is computed per candidate in lookup.py instead.
MONEY = [
    "receipts",
    "disbursements",
    "cash_on_hand_end_period",
    "individual_itemized_contributions",
]
COLUMNS = [
    "candidate_id", "name", "party", "party_full", "office", "state", "election_year",
] + MONEY


def fetch_candidate_totals(client, cycle=2024, office="H", state=None, max_pages=3):
    params = {"election_year": cycle, "office": office, "sort": "-receipts"}
    if state:
        params["state"] = state
    rows = list(client.paginate("candidates/totals", max_pages=max_pages, **params))
    df = pd.DataFrame(rows)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[COLUMNS].copy()
    df[MONEY] = df[MONEY].apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


def small_donor_share(df):
    # unitemized means the donor gave $200 or less in the cycle
    small = df["individual_unitemized_contributions"]
    total = small + df["individual_itemized_contributions"]
    return (small / total.where(total > 0)).fillna(0)


def top_n(df, n=10, column="receipts"):
    return df.sort_values(column, ascending=False).head(n).reset_index(drop=True)


def summarize_by_party(df):
    out = df.groupby("party", dropna=False).agg(
        candidates=("candidate_id", "nunique"),
        total_receipts=("receipts", "sum"),
        total_disbursements=("disbursements", "sum"),
    ).reset_index()
    return out.sort_values("total_receipts", ascending=False).reset_index(drop=True)
