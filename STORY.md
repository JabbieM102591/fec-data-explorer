# What the data says

I use this file to keep the findings I get from running the tool. Every number here
should come from a command I ran, with the date next to it.

## Commands I ran

    python -m fecdata totals --cycle 2024 --office H --state DC
    python -m fecdata totals --cycle 2024 --office S
    python -m fecdata candidate "NORTON" --cycle 2024
    python -m fecdata committee "LOCKHEED MARTIN" --cycle 2024

## Questions

1. How much of a race's money comes from small donors?
2. Is fundraising spread out or held by a few candidates (HHI and Gini)?
3. Does a corporate PAC split its giving between parties, and how sure am I?

## Findings

Finding 1: Campaign Receipt Distribution Among 2024 U.S. House Candidates in Washington, D.C.
Command: python -m fecdata totals --cycle 2024 --office H --state DC
Date run: 2026-10-20

                            name party state  receipts  small_donor_share
        NORTON, ELEANOR HOLMES   DEM    DC  307917.0                0.0
              A BROWN, MICHAEL   IND    DC   34785.0                0.0
               WILLIAMS, KELLY   DEM    DC   23325.0                0.0
          WATTS, HELCHIC KOTON   OTH    DC       0.0                0.0
ALEXANDER, MYRTLE PATRICIA DR.   REP    DC       0.0                0.0
               FREEMAN, KYMONE   OTH    DC       0.0                0.0
              MALONE, JOAN F M   REP    DC       0.0                0.0

Receipts across candidates
  n = 3, total = $366,027
  mean $122,009 vs median $34,785 (ratio 3.5)
  median 95% CI: $23,325 to $307,917
  HHI 7,208 (0 to 10,000), Gini 0.518

Finding 2: Campaign Receipt Distribution Among 2024 U.S. Senate Candidates
Command: python -m fecdata totals --cycle 2024 --office S
Date run: 2026-10-20

                      name party state     receipts  small_donor_share
CRUZ, RAFAEL EDWARD  TED   REP    TX 107113865.62                0.0
          BROWN, SHERROD   DEM    OH 103336340.79                0.0
          TESTER, R. JON   DEM    MT  98066475.74                0.0
           ALLRED, COLIN   DEM    TX  94674182.67                0.0
    CASEY, ROBERT P. JR.   DEM    PA  64886501.07                0.0
          GALLEGO, RUBEN   DEM    AZ  64657199.96                0.0
            TRONE, DAVID   DEM    MD  63833136.59                0.0
          BALDWIN, TAMMY   DEM    WI  59595651.15                0.0
            ROSEN, JACKY   DEM    NV  52192355.94                0.0
         SLOTKIN, ELISSA   DEM    MI  51937060.20                0.0

Receipts across candidates
  n = 255, total = $1,711,792,648
  mean $6,712,912 vs median $142,864 (ratio 47.0)
  median 95% CI: $68,293 to $355,613
  HHI 286 (0 to 10,000), Gini 0.850

Finding 3: Candidate Lookup and Campaign Finance Summary for 2024
Command: python -m fecdata candidate "NORTON" --cycle 2024
Date run: 2026-10-20

1. H6CT02121  NORTON, ANDREW MCCALL  REP  H-CT
2. H8CA35065  NORTON, BARRY  DEM  H-CA
3. H6GA07197  NORTON, CASEY  DEM  H-GA
4. P20000873  NORTON, CHRISTOPHER B (CHRIS)  DEM  P-US
5. H0DC00058  NORTON, ELEANOR HOLMES  DEM  H-DC

NORTON, ANDREW MCCALL (2024)
  Receipts:      $0
  Disbursements: $0
  Cash on hand:  $0
  Small-donor share of individual money: 0.0%

Finding 4: Political Contributions by the Lockheed Martin Corporation Employees’ Political Action Committee in 2024
Command: python -m fecdata committee "LOCKHEED MARTIN" --cycle 2024
Date run: 2026-10-20

1. C00303024  LOCKHEED MARTIN CORPORATION EMPLOYEES' POLITICAL ACTION COMMITTEE  type=PAC - Qualified

LOCKHEED MARTIN CORPORATION EMPLOYEES' POLITICAL ACTION COMMITTEE: top recipients in 2024
                                           recipient_name   total  gifts
                            REPUBLICAN NATIONAL COMMITTEE 60000.0      2
                            DEMOCRATIC NATIONAL COMMITTEE 60000.0      2
              DEMOCRATIC CONGRESSIONAL CAMPAIGN COMMITTEE 45000.0      1
             REPUBLICAN PARTY OF FLORIDA - HOUSE MAJORITY 10000.0      1
                               MIKE JOHNSON FOR LOUISIANA  6000.0      2
                                   TIM SHEEHY FOR MONTANA  5000.0      1
                                         SENATE EAGLE PAC  5000.0      2
CA LUV PAC (CALIFORNIA LEADERSHIP UNITED FOR VICTORY PAC)  5000.0      1
                                             BLUE HEN PAC  5000.0      2
                                  BIG SKY OPPORTUNITY PAC  5000.0      1

Giving by recipient party:
recipient_party    total  gifts  share
        Unknown 399500.0    122  0.400
            REP 356000.0    212  0.356
            DEM 242000.0    164  0.242
            IND   2500.0      2  0.002

Size of individual gifts
  n = 481, total = $1,028,500
  mean $2,138 vs median $1,000 (ratio 2.1)
  median 95% CI: $1,000 to $1,000
  HHI 84 (0 to 10,000), Gini 0.427
  Dollars to REP: 35.2% (95% CI 27.2% to 43.9%)

## Related work

The GW OSPO PALS repository has FEC data and visualizations that I looked at for ideas.
FEC bulk data: https://www.fec.gov/data/browse-data/?tab=bulk-data
