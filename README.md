# FEC Data Explorer

[![CI](https://github.com/JabbieM102591/fec-data-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/JabbieM102591/fec-data-explorer/actions)

I built this Python tool and short report to look at money in U.S. politics using the Federal Election Commission's open data. I made it for the Civic Tech DC x GW OSPO Hackathon and the GW Open Source Project Awards.

## Abstract

Campaign finance data is public, but the raw filings are hard for most people to read. I wrapped the openFEC API in a small command line tool that answers three plain questions: who raises the most money in a race, where one candidate's money comes from, and who a PAC or corporate committee gives to. Donation data is very skewed, so I report more than totals. Each run also shows me the mean against the median, two concentration measures (HHI and the Gini coefficient), and bootstrap confidence intervals, so a comparison comes with a sense of how uncertain it is. On the 2024 data I found that the ten biggest Senate fundraisers raised about 44% of all Senate money, and that about 40% of one corporate PAC's giving went to recipients with no party on record.

## 1. Why I built this

I am a statistics student, and I wanted a project where the numbers connect to something real. Money in politics fits. The FEC publishes the filings, but a journalist, a classmate or a curious voter should not have to learn the API before asking a simple question. The hackathon offered three directions: tell a story with the data, connect corporate PAC data to voting scorecards, or build tools on the openFEC API. My project is mostly the third, with a small start on the first. I did not get to the scorecard work, so I list it under what I want to add next.

## 2. Data

All of my data comes from the openFEC API at https://api.open.fec.gov/developers/. I use these endpoints:

- candidates/totals for fundraising totals by candidate, office and state
- candidates/search and candidate/{id}/totals to find and profile one candidate
- schedules/schedule_a/by_size and by_employer for a candidate's individual donations
- committees to find PACs and corporate committees by name
- schedules/schedule_b for itemized disbursements, filtered to contributions

The FEC also publishes bulk files at https://www.fec.gov/data/browse-data/?tab=bulk-data. I have not used them yet.

## 3. Methods

Small-donor share is the unitemized individual money divided by all individual money. Unitemized means donors who gave $200 or less in the cycle. I found out the hard way that the FEC's multi-candidate totals endpoint does not report unitemized money, so I get the share from each candidate's own totals record. My candidate command shows it, and my totals command shows it for the top fundraisers only.

Mean and median. A few very large gifts pull the mean up while the median stays near a typical gift, so I use the ratio of mean to median as a quick check of skew.

HHI is the sum of squared shares times 10,000. With N equal holders it is 10,000 divided by N, and with one holder it is 10,000. I use it on fundraising across candidates.

Gini coefficient measures inequality from 0 (perfectly even) toward 1 (a few hold most). With values sorted from smallest to largest, x1 to xn, it is 2 times the sum of i times xi, divided by n times the sum of xi, minus (n+1)/n.

Bootstrap confidence intervals. I resample the data with replacement 2,000 times, recompute the statistic each time, and take the 2.5th and 97.5th percentiles. I use this for the median amount and for the share of dollars going to one party, resampling whole gifts. I fixed the random seed at 42 so my results repeat.

I use only positive amounts in these statistics. Refunds show up as negative numbers in the filings, and I leave them out.

## 4. The tool

To install it:

    git clone https://github.com/JabbieM102591/fec-data-explorer.git
    cd fec-data-explorer
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    export FEC_API_KEY=your_key

On Windows in Git Bash, I activate with source .venv/Scripts/activate. In PowerShell, I use .venv\Scripts\Activate.ps1 and set the key with $env:FEC_API_KEY="your_key". A free key is available at https://api.data.gov/signup/. Without one the tool uses DEMO_KEY, which is rate limited.

My three commands:

    python -m fecdata totals --cycle 2024 --office H --state DC
    python -m fecdata candidate "NORTON" --cycle 2024 --pick 5
    python -m fecdata committee "LOCKHEED MARTIN" --cycle 2024

The totals command lists the top fundraisers with their small-donor share and prints the statistics for receipts across all candidates returned. It prints a warning when there are fewer than 10 values, because the statistics are not reliable then. The candidate command shows receipts, spending, cash on hand, small-donor share, donations by size and top donor employers. The committee command shows the biggest recipients of a committee's contributions, a split by recipient party, gift statistics, and a bootstrap interval for the share going to the largest party.

A name search can return several matches, so I add --pick 2 (or another number) to choose one. Every run writes CSV files and PNG charts to an outputs folder, and the file names include the office, state and year so one run does not overwrite another.

My code layout:

- fecdata/client.py handles the API and paging
- fecdata/analysis.py builds candidate tables
- fecdata/lookup.py searches candidates and committees and cleans the results
- fecdata/stats.py holds HHI, Gini, mean and median, and the bootstrap
- fecdata/cli.py is the command line
- tests/ has my 24 unit tests, which use fake API responses

## 5. What I found

I ran my commands on live 2024 data on 2026-10-21. The full write-up is in STORY.md. The headlines:

- Among 255 Senate candidates who reported money, the mean was $6.7 million and the median was $142,864, a ratio of 47. The Gini was 0.85, and the ten biggest fundraisers raised 44.4% of the $1.71 billion total.
- In the DC House race, Eleanor Holmes Norton raised about 84% of the money raised by all candidates.
- A Lockheed Martin employees' PAC gave $1,028,500 in 481 contributions. About 40% of the dollars went to recipients with no party on record, so I only compare the parties among the rest.

## 6. Reproducing my results

I ran the commands listed in STORY.md. To reproduce them, use your own API key. The results depend on the date you run them, because the FEC keeps updating filings. I recommend writing the date next to any number you quote.

## 7. Limitations

- I tested my code with fake responses and then with live runs on the commands above. I still recommend checking any number you quote against fec.gov.
- Name searches can match more than one person or committee, so I print the ID of each match and let you choose with --pick.
- My tool reads a set number of pages, so a very large committee is a sample of itemized gifts, not a full count.
- Schedule B only covers itemized contributions. Many recipients, including party committees and other PACs, have no party on record, so I show that money as Unknown. I report that share separately and compute the party share only among recipients that have a party.
- I leave refunds (negative amounts) out of the party split and gift statistics.
- Employer names are as donors typed them, so one employer can appear under slightly different spellings. I remove placeholders such as NOT EMPLOYED and SELF-EMPLOYED from the employer list, but I do not merge spellings.
- My statistics describe the data returned. They do not show why anyone gave, and they do not show that money caused a vote.
- Corporate PACs are funded by employees and give on behalf of a company, so linking a PAC to a company needs care.

## 8. What went wrong along the way

My first version reported a small-donor share of 0.0% for every candidate, including ones with $100 million in receipts. When I ran it on live data, I realized the multi-candidate endpoint I used does not return unitemized contributions, so my code filled in zeros. I fixed it by looking up the share from each candidate's own totals record, and I added a test so that mistake cannot come back. I also learned that a name search is not sorted by relevance: my first Norton search picked the wrong person.

## 9. Tests

    pytest

My tests cover the statistics (known values for HHI and Gini, a repeatable bootstrap), paging, the table builders, and the command line. GitHub Actions runs them on every push.

## 10. What I want to add next

- Join PAC giving with public scorecards for members of Congress on issues like LGBTQ+ rights, abortion rights and gun rights
- Support FEC bulk data so large analyses do not depend on the API
- A map of a candidate's money by state
- Label national party committees and merge employer names that are spelled differently

## 11. Contributing

See CONTRIBUTING.md and CODE_OF_CONDUCT.md. Issues labeled good first issue are a good place to start, and I would love the help.

## 12. License and credits

MIT license, see the LICENSE file. The data belongs to the Federal Election Commission and is public. I want to thank the GW Open Source Program Office and its director David Lippert, Civic Tech DC, and the GW PALS repository, which gave me ideas about how to present this data.