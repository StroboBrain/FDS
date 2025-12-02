import pandas as pd
import numpy as np
from scipy import stats

class DifferentialPrivacyAnalyzer:

    # Initialize with a pandas DataFrame
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def laplace_mech(self, value, sensitivity, epsilon) -> float:
        scale = sensitivity / epsilon
        # always symmetric at zero, hardcoded first parameter 
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def calculate_scale(self, sensitivity: float, epsilon: float) -> float:
        return sensitivity / epsilon

    def dp_count_over_value(self, column, value) -> int:
        true_count = (self.df[column] == value).sum()
        return true_count

    def dp_contingency_table(self, col1, col2) -> pd.DataFrame:
        return pd.crosstab(self.df[col1], self.df[col2])
    
    def dp_add_noise_to_contingency_table(self, contingency_table: pd.DataFrame, epsilon: float, round_to_int: bool) -> pd.DataFrame:
        # Create a copy to avoid modifying the original table
        noisy_table = contingency_table.copy().astype(float)

        # Sensitivity is always 1 fpr contingency tables
        scale = self.calculate_scale(1, epsilon)
        for row in noisy_table.index:
            for col in noisy_table.columns:
                noise = np.random.laplace(0, scale)
                # Add noise to each cell
                noisy_table.at[row, col] += noise
        # Optionally round to integer
        if round_to_int:
            noisy_table = noisy_table.round().astype(int)
        return noisy_table
    
    # Simple scroring function, where the count is the score
    def score(self, occupation):
        return (self.df['Occupation'] == occupation).sum()
    
    def most_common_noisy(self, epsilon: float, collumn: str) -> str:
        collumn = self.df['Occupation'].unique()
        best_score = -float('inf')
        best = None
        sensitivity = 1  # Each person affects count of their occupation by at most 1
        for temp in collumn:
                true_count = self.score(temp)
                noisy_count = true_count + np.random.laplace(0, sensitivity/epsilon)
                if noisy_count > best_score:
                    best_score = noisy_count
                    best = temp
        return best
    
    def dp_sum_capgain(epsilon: float, df) -> float:
        # Clipping parameter B (max contribution per individual)
        B = 15000  
        # Clip each individual's capital gain to the range [0, B]
        clipped = df['Capital Gain'].clip(upper=B)
        # Sensitivity is B (one person can change the clipped sum by at most B)
        sensitivity = B
        noisy_sum = clipped.sum() + np.random.laplace(0, sensitivity/epsilon)
        return noisy_sum





# Helper function to run all tasks
def nextExercise():
    print("\n" + "-"*90 + "\n")


def main():
    adult_df = pd.read_csv("adult_with_pii.csv")
    analyzer = DifferentialPrivacyAnalyzer(adult_df)

    count_over_29 = analyzer.dp_count_over_value("Age", 29)
    # Sensitivity for count query is  always 1, because adding or removing one individual can change the count by at most 1.
    # Epsilon is set to ln(2) based on the exercise privacy requirements.
    noisy_count = analyzer.laplace_mech(count_over_29, sensitivity=1, epsilon=np.log(2))

    nextExercise()
    print("Ex 1:")
    print(f"1 a) Sensitivity of count query is 1.")
    print(f"True count of age 29: {count_over_29}")
    print(f"Noisy count: {noisy_count}")

    contingency_table= analyzer.dp_contingency_table("Relationship", "Race")
    contingency_table_noisy = analyzer.dp_add_noise_to_contingency_table(contingency_table, 0.3, True)

    nextExercise()
    print("Ex 2:")
    print(f"2 b) Contingency table between 'Relationship' and 'Race':")
    print(contingency_table)
    print(f"Noisy Contingency table with differential privacy:")
    print(contingency_table_noisy)

    nextExercise()
    print("Ex 3:")
    # Epsilon is set to 0.05 based on the exercise privacy requirements.
    most_common_occupation = analyzer.most_common_noisy(epsilon=0.05, collumn="Occupation")
    print(f"Most common occupation with noisy: {most_common_occupation}")

    nextExercise()
    print("Ex 4:")
    max_capgain = adult_df['Capital Gain'].max()
    min_capgain = adult_df['Capital Gain'].min()
    print(f"Max Capital Gain: {max_capgain}, Min Capital Gain: {min_capgain}")



    nextExercise()
    print("Ex 5:")







if __name__ == "__main__":
    main()
