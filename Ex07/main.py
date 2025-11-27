import pandas as pd
import numpy as np
from scipy import stats



def laplace_mech(v, sensitivity, epsilon):
    pass


def dp_count_over_29(adult_df):
    pass


def dp_contingency_table(df, col1, col2, epsilon):
    pass


def dp_relationship_race(adult_df):
    pass


def score(df):
    pass


def most_common_occupation(df, epsilon):
    pass


def dp_sum_capgain(df, epsilon):
    pass



def differencing_attack(df):
    pass


def dp_differencing_attack(df, epsilon):
    pass


def main():
    adult_df = load_adult_dataset()


# Helper function to run all tasks

def load_adult_dataset(path="adult_with_pii.csv"):
    """Load the adult dataset from CSV."""
    return pd.read_csv(path)


if __name__ == "__main__":
    main()