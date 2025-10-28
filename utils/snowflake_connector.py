import os
import pandas as pd

def get_snowflake_dfs():
    try:
        import snowflake.connector
    except Exception as e:
        raise RuntimeError("snowflake-connector not installed") from e
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE","COMPUTE_WH"),
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ.get("SNOWFLAKE_SCHEMA","PUBLIC"),
    )
    cur = conn.cursor()
    def fetch_df(sql):
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=cols)
    clinical = fetch_df("SELECT * FROM CLINICAL")
    spatial = fetch_df("SELECT * FROM SPATIAL_EXPRESSION")
    genes = fetch_df("SELECT * FROM GENES")
    cur.close(); conn.close()
    return clinical, spatial, genes
