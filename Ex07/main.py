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
        true_count = (self.df[column] > value).sum()
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
    
    def most_common_occupation(self, epsilon: float) -> str:
        categories = self.df["Occupation"].unique()
        sensitivity = 1  # Each person has only one occupation
        
        # Compute true scorees
        scores = []

        for c in categories:
            score_val = self.score(c)
            scores.append(score_val)

        # Compute exponential mechanism weights for each category
        weights = [np.exp((epsilon * s) / (2)) for s in scores]
        total_weight = sum(weights)
        # Normalize weights to get probabilities
        probabilities = [w / total_weight for w in weights]
        
        # Randomly select a category according to the probability distribution
        chosen_category = np.random.choice(categories, p=probabilities)
        return chosen_category
    
    def dp_sum_capital_gain(self, epsilon: float) -> float:
        # Compute clipping threshold (99th percentile)
        q99 = self.df["Capital Gain"].quantile(0.99)

        # Clip values (replace values above q99 with q99)
        clipped = self.df["Capital Gain"].clip(upper=q99)

        # Sensitivity = clipping bound
        sensitivity = q99

        # Add Laplace noise
        noise = np.random.laplace(0, sensitivity / epsilon)

        noisy_sum = clipped.sum() + noise
        return noisy_sum, clipped.max()

    def clip_column(column: str, percentage: float) ->pd.DataFrame:
        lower_bound = column.quantile(percentage / 2)
        upper_bound = column.quantile(1 - (percentage / 2))
        return column.clip(lower=lower_bound, upper=upper_bound)
    
    def dp_differencing_attack(self, epsilon: float):
        sensitivity = 103
        # Select the age of the person
        age = self.df.loc[self.df['Name'] == 'Karrie Trusslove', 'Age'].iloc[0]

        # Generate Laplace noise
        noise = np.random.laplace(0, sensitivity / epsilon)

        noisy_age = age + noise

        return noisy_age
    
# Helper function
def nextExercise():
    print("\n" + "-"*90 + "\n")

# Runs the functions for the excercise
def main():
    adult_df = pd.read_csv("adult_with_pii.csv")
    analyzer = DifferentialPrivacyAnalyzer(adult_df)

    count_over_29 = analyzer.dp_count_over_value("Age", 29)
    # Sensitivity for count query is  always 1, because adding or removing one individual can change the count by at most 1.
    # Epsilon is set to ln(2) based on the exercise privacy requirements.
    noisy_count = analyzer.laplace_mech(count_over_29, sensitivity=1, epsilon=np.log(2))

    nextExercise()
    print("1:")
    print(f"1 a) Sensitivity of count query is 1.")
    print(f"True count of age 29: {count_over_29}")
    print(f"Noisy count: {noisy_count}")

    contingency_table= analyzer.dp_contingency_table("Relationship", "Race")
    contingency_table_noisy = analyzer.dp_add_noise_to_contingency_table(contingency_table, 0.3, True)

    nextExercise()
    print("2:")
    print(f"2 b) Contingency table between 'Relationship' and 'Race':")
    print(contingency_table)
    print(f"Noisy Contingency table with differential privacy:")
    print(contingency_table_noisy)

    nextExercise()
    print("3:")
    # Epsilon is set to 0.05 based on the exercise privacy requirements.
    most_common_occupation = analyzer.most_common_occupation(epsilon=0.05)
    print(f"Most common occupation with noisy: {most_common_occupation}")
    nextExercise()
    print("4:")
    max_capgain = adult_df['Capital Gain'].max()
    min_capgain = adult_df['Capital Gain'].min()
    print(f"Max Capital Gain: {max_capgain}, Min Capital Gain: {min_capgain}")
    print(f"Modifying Dataset by clipping the top capital gain 1%")
    sum_capgain_noisy, clipped_max = analyzer.dp_sum_capital_gain(epsilon=0.04)
    print(f"Clipped max Capital Gain (99th percentile): {clipped_max}")
    print(f"Noisy sum of Capital Gain after clipping: {sum_capgain_noisy}")

    nextExercise()
    print("5:")
    max_age = adult_df['Age'].max()
    print(f"Sensitivity is max_age {max_age}")
    # No epsilon is specified in the excercise so 0.05 was used (No usful value given)
    noisy_age_diff = analyzer.dp_differencing_attack(epsilon=0.05)
    print(f"Noisy result for age sum difference when removing 'Karrie Trusslove': {noisy_age_diff}")
    nextExercise()

if __name__ == "__main__":
    main()