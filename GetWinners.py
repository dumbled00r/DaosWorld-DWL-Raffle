import math
from decimal import Decimal

import numpy as np
import pandas as pd


def raffle_for_burners(snapshot_file="DWL_Burners_snapshot.csv"):
    """
    Conducts a weighted raffle where participants with <1 DWL burned
    have a chance proportional to their burned amount.

    Args:
        snapshot_file (str): Path to the DWL_Burners_snapshot.csv file.
        num_winners (int): Number of winners to select from the raffle pool.

    Returns:
        str: Path to the CSV file with the winners.
    """
    df = pd.read_csv(snapshot_file)

    # Set the random seed
    np.random.seed(26423963)

    snipers = []
    df = df[~df["sender_address"].isin(snipers)]

    df["total_burned"] = df["total_burned"].astype(str).apply(Decimal)
    df["total_burned_dwl"] = df["total_burned"] / Decimal(1e18)

    # get guaranteed list // those who burned 1M $DWL or more
    guaranteed_winners = df[df["total_burned_dwl"] >= 1e6]["sender_address"].tolist()
    # get non-guaranteed list // those who burned less than 1M $DWL
    raffle_pool = df[df["total_burned_dwl"] < 1e6]

    total_num_winners = math.ceil(sum(raffle_pool["total_burned_dwl"]) / Decimal("1e6"))

    weights = raffle_pool["total_burned_dwl"]
    # normalize weights
    weights = weights / weights.sum()
    print(f"Sum of probabilities: {sum(weights)}")
    winners_index = np.random.choice(
        raffle_pool.index, size=total_num_winners, replace=False, p=weights
    )

    raffle_winners_addresses = raffle_pool.loc[winners_index, "sender_address"].tolist()

    final_winners = list(guaranteed_winners + raffle_winners_addresses)

    final_winners_df = pd.DataFrame(
        {
            "sender_address": final_winners,
            "total_burned_dwl": [
                df.loc[df["sender_address"] == addr, "total_burned_dwl"].values[0]
                for addr in final_winners
            ],
            "win_type": [
                "guaranteed" if addr in guaranteed_winners else "raffle"
                for addr in final_winners
            ],
        }
    )

    # Save winners to a CSV file
    output_file = "winners.csv"
    final_winners_df.to_csv(output_file, index=False)

    print(f"Raffle completed. Winners saved to {output_file}.")
    return output_file


if __name__ == "__main__":
    raffle_for_burners()
