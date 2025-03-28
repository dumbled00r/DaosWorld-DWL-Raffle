import os
from time import sleep

import pandas as pd
from dotenv import load_dotenv
from dune_client.client import DuneClient
from dune_client.models import ExecutionState
from dune_client.query import QueryBase
from dune_client.types import QueryParameter

load_dotenv()
DUNE_API_KEY = os.environ["DUNE_KEY"]

dune = DuneClient(api_key=DUNE_API_KEY)

QUERY_ID = 4530579  # query id for getting burners https://dune.com/queries/4530579


block_number = 27372303  # modify this to snapshot at a specific block number
burn_address = "0xDead000000000000000000000000000000000009"
token_address = "0x41f86a22c05500cb62ddc82b77c01c7c5912fa37"  # $DWL


def getBurners():
    """FUNCTION TO EXPORT BURNERS TO CSV"""
    try:

        query = QueryBase(
            name="getBurners",
            query_id=QUERY_ID,
            params=[
                QueryParameter.number_type(name="block_number", value=block_number),
                QueryParameter.text_type(
                    name="burn_address",
                    value=burn_address,
                ),
                QueryParameter.text_type(name="token_address", value=token_address),
            ],
        )
        job_id = dune.execute_query(query).execution_id
        # status = dune.get_execution_status(job_id)
        # # get the result

        results = dune.get_execution_results(job_id)
        while results.state != ExecutionState.COMPLETED:
            try:
                results = dune.get_execution_results(job_id)
                sleep(1)
            except Exception:
                print("Too many requests 429, sleep for a while...")
                sleep(5)

        # print(result)
        df = pd.DataFrame(results.result.rows)

        df.to_csv(f"DWL_Burners_snapshot.csv", index=False)

        print("Burners exported to csv")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    getBurners()
