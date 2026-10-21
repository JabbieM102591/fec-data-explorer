# What I found in the data

These are the findings I got by running my own FEC Data Explorer on live OpenFEC data. I ran every command on 2026-10-21. The FEC keeps updating filings, so if you rerun them later you may see slightly different numbers.

## Finding 1: Senate fundraising in 2024 was extremely uneven

Command: python -m fecdata totals --cycle 2024 --office S

I found 255 Senate candidates who reported money, together $1,711,792,648. The average candidate raised $6.7 million, but the median candidate raised only $142,864, so the mean is 47 times the median. The Gini coefficient is 0.850, which tells me a few candidates hold most of the money.

The ten biggest fundraisers (Cruz, Brown, Tester, Allred, Casey, Gallego, Trone, Baldwin, Rosen and Slotkin) raised $760.3 million together. That is 44.4% of all the money, from under 4% of the candidates. The top fundraiser, Ted Cruz, raised $107.1 million, or 6.3% of the total.

My HHI is 286 on a scale of 0 to 10,000. That looks low, but it is mostly because there are so many candidates. If all 255 had raised the same amount it would be 39, so the money is about seven times more concentrated than an even split.

## Finding 2: Small donors matter a lot for the biggest Senate campaigns, with one exception

Command: python -m fecdata totals --cycle 2024 --office S

Among the ten top fundraisers, nine got between 33.9% and 48.4% of their individual money from donors giving $200 or less. Allred was highest at 48.4% and Gallego was close behind at 45.4%. David Trone was the exception at 18.0%. I have not checked why his share is so much lower, so I am not claiming a reason.

## Finding 3: In the DC House race, one candidate raised most of the money

Command: python -m fecdata totals --cycle 2024 --office H --state DC

Eleanor Holmes Norton raised $307,917 of the $366,027 raised by all DC House candidates, about 84.1%. Four other candidates reported $0. Only three candidates reported money, so I do not rely on the summary statistics for this race, and my tool warns about that.

## Finding 4: Norton's individual money came mostly from large donations

Command: python -m fecdata candidate "NORTON" --cycle 2024 --pick 5

The FEC's size breakdown shows $79,667 of individual contributions. I calculate that 9.2% came from donors giving $200 or less, and 49.1% came from donors giving $2,000 or more. Donations of $1,000 or more made up 72.9% of the total. My tool's headline small-donor share is 8.9%. It comes from a different FEC record, which is why it differs a little from my 9.2%.

The top donor employer was The Donohoe Companies Inc. with $16,550 from 14 contributions. A second entry spelled "Donohue" has $3,500 from 4 contributions. They look like two spellings of the same name, which would make $20,050 from 18 contributions, but I have not verified that, so I keep them separate. The FEC reports no count for the $200-and-under bucket, so I do not use it.

## Finding 5: A corporate PAC gave to both parties, but 40% of its money cannot be placed on a party

Command: python -m fecdata committee "LOCKHEED MARTIN" --cycle 2024 --pick 1

The Lockheed Martin Corporation Employees' Political Action Committee gave $1,028,500 in 481 contributions in 2024. The typical gift was $1,000 (median), while the mean was $2,138 because of some much larger gifts. For example, it gave $45,000 in one gift to the DCCC and $60,000 in total to each of the national party committees (two gifts each).

By recipient party, 35.2% of the dollars went to Republican recipients, 24.4% to Democratic recipients, and 0.2% to independents. The other 40.2% went to recipients with no party on record. That group includes the national party committees and other PACs, so I cannot tell the true split between the parties from this data. Among only the recipients that do have a party, 58.9% of the dollars went to Republicans (95% bootstrap interval 47.6% to 69.8%). I treat that as a description of the labeled money, not of the PAC's overall giving.

## What I would do next

I want to label the national committees and leadership PACs, merge employer names that are spelled differently, and bring in the scorecard data from the hackathon prompt so I can compare PAC giving with voting records.

## My limits

My statistics describe the data the FEC returned. They do not show why anyone gave, and they do not show that money caused any vote. My tool reads a limited number of pages for large committees. I recommend checking any number against fec.gov before you quote it.

## Related work

I looked at the GW OSPO PALS repository, which has FEC data and visualizations, for ideas.
FEC bulk data: https://www.fec.gov/data/browse-data/?tab=bulk-data
