#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
Used to aggregate tables found in PORTAL-RAW in snowflake SAGE database
"""


from dotenv import dotenv_values
import snowflake.connector
import pandas as pd
import numpy as np
from datetime import datetime


# there is probably a better way to do this. But this works for now
data_tables = ["AD", "ELITE", "GENIE", "HTAN", "NF", "PSYCHENCODE"]
table_names = ["SAGE.PORTAL_RAW." + d for d in data_tables]

config = dotenv_values("../.env")
conn = snowflake.connector.connect(
    user=config["USER"],
    account=config["ACCOUNT_IDENTIFIER"],
    # FOR browser-based SSO for authentication since account uses Google account for login. It is organization-username
    authenticator="externalbrowser",
    warehouse=config["WAREHOUSE"],
    database=config["DATABASE"],
    role=config["ROLE"],
    login_timeout=60,
    network_timeout=30,
    socket_timeout=10,
)

# create cursor
cur = conn.cursor()

# Try to join all the tables together

sf_tables = {}

for t in table_names:
    query = f"""
        SELECT * FROM {t}
    """

    cur.execute(query)

    # Retrieve results
    df = pd.concat([d for d in cur.fetch_pandas_batches()])
    df = df.reset_index(drop=True)
    df["TABLE"] = t
    sf_tables[t] = df

cur.close()

comb_df = pd.concat(sf_tables.values()).reset_index(drop=True)

original_shape = comb_df.shape
original_cols = sorted(comb_df.columns)
comb_df = comb_df.dropna(how="all", axis=1)
# removing empty lists and changing all nonetypes to nans
comb_df = comb_df.replace("[]", np.nan).fillna(value=np.nan)
# cleanup lists and values for new lines, double spaces and quotes
comb_df = comb_df.apply(lambda x: x.str.replace('\n|\s+|"', "", regex=True), axis=1)
# drop empty columns
comb_df = comb_df.dropna(how="all", axis=1)
comb_df = comb_df[sorted(comb_df.columns)]

print(
    f"""
|ORIGINAL|NEW|
|---|---|
|{original_shape}|{comb_df.shape}|
"""
)

comb_df.to_csv(f"../data/portal-data-raw-{datetime.now().strftime('%Y%m%d')}.csv")
