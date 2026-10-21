import pandas as pd

from fecdata import lookup
from fecdata.analysis import fetch_candidate_totals, small_donor_share, summarize_by_party, top_n
from fecdata.cli import build_parser
from fecdata.client import FECClient


class Resp:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class PageSession:
    def get(self, url, params=None, timeout=None):
        return Resp({"results": [{"id": params["page"]}], "pagination": {"pages": 2}})


class KeysetSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(dict(params))
        if "last_index" in params:
            return Resp({"results": [], "pagination": {}})
        return Resp({"results": [{"x": 1}],
                     "pagination": {"last_indexes": {"last_index": "9"}}})


class TotalsClient:
    """Fake client that mimics the multi-candidate totals endpoint (no unitemized field)."""

    def paginate(self, path, max_pages=1, **params):
        yield {"candidate_id": "A", "name": "A", "party": "DEM", "receipts": "300",
               "disbursements": "200", "individual_itemized_contributions": "80"}

    def get(self, path, **params):
        return {"results": [{"individual_unitemized_contributions": 20,
                             "individual_itemized_contributions": 80}]}


def sample():
    return pd.DataFrame({
        "candidate_id": ["A", "B", "C"],
        "party": ["DEM", "REP", "DEM"],
        "receipts": [300.0, 200.0, 100.0],
        "disbursements": [250.0, 150.0, 90.0],
        "individual_itemized_contributions": [75.0, 100.0, 0.0],
        "individual_unitemized_contributions": [25.0, 0.0, 0.0],
    })


def test_small_donor_share():
    assert list(small_donor_share(sample())) == [0.25, 0.0, 0.0]


def test_top_n():
    assert list(top_n(sample(), 2)["candidate_id"]) == ["A", "B"]


def test_summarize_by_party():
    s = summarize_by_party(sample())
    dem = s[s["party"] == "DEM"].iloc[0]
    assert dem["candidates"] == 2 and dem["total_receipts"] == 400.0


def test_fetch_totals_has_no_made_up_small_donor_column():
    df = fetch_candidate_totals(TotalsClient(), 2024, "S")
    assert "individual_unitemized_contributions" not in df.columns
    assert df.loc[0, "receipts"] == 300.0


def test_small_donor_share_for_one_candidate():
    assert lookup.small_donor_share_for(TotalsClient(), "A", 2024) == 0.2


def test_paginate_stops_at_last_page():
    client = FECClient(api_key="x", session=PageSession())
    assert [r["id"] for r in client.paginate("anything")] == [1, 2]


def test_keyset_paginate_passes_last_index():
    session = KeysetSession()
    rows = list(FECClient("k", session).keyset_paginate("schedules/schedule_b", a=1))
    assert rows == [{"x": 1}]
    assert session.calls[1]["last_index"] == "9"


def test_contributions_and_summaries():
    rows = [
        {"recipient_name": "A", "disbursement_amount": 1000,
         "recipient_committee": {"party": "DEM"}},
        {"recipient_name": "A", "disbursement_amount": 500,
         "recipient_committee": {"party": "DEM"}},
        {"recipient_name": "B", "disbursement_amount": 1500, "recipient_committee": None},
    ]
    df = lookup.contributions_to_df(rows)
    top = lookup.summarize_recipients(df, 5)
    assert top["total"].sum() == 3000
    split = lookup.party_split(df)
    assert set(split["recipient_party"]) == {"DEM", "Unknown"}
    assert abs(split["share"].sum() - 1.0) < 0.01


def test_party_split_leaves_out_refunds():
    df = pd.DataFrame({
        "recipient_name": ["A", "A", "B"],
        "recipient_party": ["DEM", "DEM", "REP"],
        "amount": [1000.0, -400.0, 1000.0],
    })
    split = lookup.party_split(df)
    dem = split[split["recipient_party"] == "DEM"].iloc[0]
    assert dem["total"] == 1000.0 and dem["gifts"] == 1


def test_clean_employers_drops_placeholders():
    df = pd.DataFrame({"employer": ["NOT EMPLOYED", "Acme Inc", "SELF-EMPLOYED", None, "Retired"],
                       "total": [5, 4, 3, 2, 1], "count": [1, 1, 1, 1, 1]})
    cleaned = lookup.clean_employers(df)
    assert list(cleaned["employer"]) == ["Acme Inc"]


def test_size_breakdown_labels():
    df = lookup.size_breakdown([{"size": 200, "total": 5, "count": 1},
                                {"size": 0, "total": 9, "count": 3}])
    assert list(df["bucket"]) == ["$200 and under", "$200.01 - $499.99"]


def test_principal_committee_id():
    assert lookup.principal_committee_id({"principal_committees": [{"committee_id": "C001"}]}) == "C001"
    assert lookup.principal_committee_id({}) is None


def test_cli_parses_subcommands():
    args = build_parser().parse_args(["committee", "Acme PAC", "--cycle", "2022"])
    assert args.command == "committee" and args.cycle == 2022
