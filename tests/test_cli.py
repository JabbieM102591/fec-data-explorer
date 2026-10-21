import matplotlib.figure

from fecdata import cli


class FakeClient:
    def paginate(self, path, max_pages=1, **params):
        for i in range(12):
            yield {"candidate_id": f"S{i}", "name": f"CAND {i}", "party": "DEM",
                   "office": "S", "state": "TX", "election_year": 2024,
                   "receipts": str(1000 * (i + 1) ** 2), "disbursements": "5",
                   "individual_itemized_contributions": "10"}

    def get(self, path, **params):
        return {"results": [{"individual_unitemized_contributions": 30,
                             "individual_itemized_contributions": 70}]}


def run_totals(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "FECClient", FakeClient)
    args = ["totals", "--office", "S", "--state", "TX", "--top", "3", "--out", str(tmp_path)]
    return cli.main(args)


def test_totals_names_files_after_the_run(tmp_path, monkeypatch):
    assert run_totals(tmp_path, monkeypatch) == 0
    names = {p.name for p in tmp_path.iterdir()}
    assert "top_receipts_S_TX_2024.png" in names
    assert "candidate_totals_S_TX_2024.csv" in names


def test_totals_survives_a_chart_that_cannot_be_saved(tmp_path, monkeypatch, capsys):
    def blocked(self, *args, **kwargs):
        raise OSError(22, "Invalid argument")

    monkeypatch.setattr(matplotlib.figure.Figure, "savefig", blocked)
    assert run_totals(tmp_path, monkeypatch) == 0
    assert "Could not save chart" in capsys.readouterr().out
