# FEC Data Explorer

[![CI](https://github.com/JabbieM102591/fec-data-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/JabbieM102591/fec-data-explorer/actions)

A Python tool and short report on money in U.S. politics, built on the Federal Election Commission's open data. I made it for the Civic Tech DC x GW OSPO Hackathon and the GW Open Source Project Awards.

## Abstract

Campaign finance data is public, but the raw filings are hard to read. This project wraps the openFEC API in a small command line tool that answers three plain questions: who raises the most money in a race, where a single candidate's money comes from, and who a PAC or corporate committee gives to. Because donation data is heavily skewed, I report more than totals. Each run also gives the mean against the median, two concentration measures (HHI and the Gini coefficient), and bootstrap confidence intervals, so a comparison comes with a sense of how uncertain it is.

## 1. Why I built this

I am a statistics student, and I wanted a project where the numbers connect to something real. Money in politics fits. The FEC publishes the filings, but a journalist, a classmate or a curious voter should not need to learn the API before asking a simple question. The hackathon gave three directions: tell a story with the data, connect corporate PAC data to voting scorecards, or build tools on the openFEC API. This repo is mostly the third, with a small start on the first. The scorecard work is on the roadmap.

## 2. Data

All data comes from the openFEC API at https://api.open.fec.gov/developers/. These endpoints are used:

- candidates/totals for fundraising totals by candidate, office and state
- candidates/search and candidate/{id}/totals to find and profile one candidate
- schedules/schedule_a/by_size and by_employer for a candidate's individual donations
- committees to find PACs and corporate committees by name
- schedules/schedule_b for itemized disbursements, filtered to contributions

The FEC also publishes bulk files at https://www.fec.gov/data/browse-data/?tab=bulk-data. I do not use them yet.

## 3. Methods

Small-donor share is the unitemized individual money divided by all individual money. Unitemized means donors who gave $200 or less in the cycle.

Mean and median. A few very large gifts pull the mean up while the median stays near a typical gift, so the ratio of mean to median is a quick check of skew.

HHI is the sum of squared shares times 10,000. With N equal holders it is 10,000 divided by N, and with one holder it is 10,000. I use it on fundraising across candidates and on gift sizes.

Gini coefficient measures inequality from 0 (perfectly even) toward 1 (a few hold most). With values sorted from smallest to largest, x1 to xn, it is 2 times the sum of i times xi, divided by n times the sum of xi, minus (n+1)/n.

Bootstrap confidence intervals. I resample the data with replacement 2,000 times, recompute the statistic each time, and take the 2.5th and 97.5th percentiles. I use this for the median amount and for the share of dollars going to one party, resampling whole gifts. The random seed is fixed at 42 so results repeat.

Only positive amounts are used in these statistics. Refunds show up as negative numbers in the filings and are left out.

## 4. The tool

Install:

    git clone https://github.com/JabbieM102591/fec-data-explorer.git
    cd fec-data-explorer
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    export FEC_API_KEY=your_key

On Windows, activate with .venv\Scripts\activate. A free key is available at https://api.data.gov/signup/. Without one the tool uses DEMO_KEY, which is rate limited.

Four commands:

    python -m fecdata totals --cycle 2024 --office H --state DC
    python -m fecdata totals --cycle 2024 --office S
    python -m fecdata candidate "NORTON" --cycle 2024
    python -m fecdata committee "LOCKHEED MARTIN" --cycle 2024

The totals command lists the top fundraisers and prints the statistics for receipts across all candidates returned. The candidate command shows receipts, spending, cash on hand, small-donor share, donations by size and top donor employers. The committee command shows the biggest recipients of a committee's contributions, a split by recipient party, gift statistics, and a bootstrap interval for the share going to the largest party.

If a search returns several matches, add --pick 2 to use the second one. Every run writes CSV files and PNG charts to an outputs folder.

Code layout:

- fecdata/client.py handles the API and paging
- fecdata/analysis.py builds candidate tables
- fecdata/lookup.py searches candidates and committees
- fecdata/stats.py holds HHI, Gini, mean and median, and the bootstrap
- fecdata/cli.py is the command line
- tests/ has the unit tests, which use fake API responses

## 5. Reproducing my results

Run the commands in STORY.md with your own API key. Results depend on the date you run them, because the FEC updates filings as they come in. Record the date next to any number you quote.

## 6. Findings

My findings and the commands that produced them are in STORY.md.

## 7. Limitations

- The code is unit tested with fake responses only. Check output against fec.gov before quoting a number.
- Name searches can match more than one person or committee, so check the ID that is printed.
- The tool reads a set number of pages, so a large committee is a sample of itemized gifts, not a full count.
- Schedule B only covers itemized contributions. When the FEC record gives no party for a recipient, that money is shown as Unknown.
- The statistics describe the data returned. They do not show why anyone gave, and they do not show that money caused a vote.
- Corporate PACs are funded by employees and give on behalf of a company, so linking one to a company needs care.

## 8. Tests

    pytest

The tests cover the statistics (known values for HHI and Gini, repeatable bootstrap), paging, and the table builders. GitHub Actions runs them on every push.

## 9. What I want to add next

- Join PAC giving with public scorecards for members of Congress on issues like LGBTQ+ rights, abortion rights and gun rights
- Support FEC bulk data so large analyses do not depend on the API
- A map of a candidate's money by state

## 10. Contributing

See CONTRIBUTING.md and CODE_OF_CONDUCT.md. Issues labeled good first issue are a good place to start.

## 11. License and credits

MIT license, see the LICENSE file. Data belongs to the Federal Election Commission and is public. Thanks to the GW Open Source Program Office and its director David Lippert, to Civic Tech DC, and to the GW PALS repository, which gave me ideas about how to present this data.
