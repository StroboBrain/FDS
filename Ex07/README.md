# TODO
Create PDF or there are no points!

# Manual
Requires Python3

Step 1: Open a terminal and navigate to the project folder Ex07
```python3
pip install -r requirements.txt      
```
Step 2: Run the main.py file

```python3
python main.py
```


# Excercise Sheet Answers
## 1 a) 
The sensitivity of a count query is always 1, because we are comparing datasets, that are different in one entry.

## 2 a)
Yes, the parallel compositions applies because we split the dataset into disjoint chunks. Each Person only contributes to one cell in this composed dataset.
## 2 b)
The number of variables in the contingency table does not increase the privacy cost, as long as each individual data appears only in one cell.
The accuracy decreases, because we noise to each entry.


## 3 a)
It is one as well, because each entry has a maximum of one occupation.
## 3 b)
Even though we add noise to multiple values, each person’s data influenced only one noisy count, so the privacy loss for any individual is bounded by ε = 0.04.

## 4 a)
There is a tradeoff between the information that is lost by clipping and the noise needed to ensure differential privacy. 

## 4 b)

## 4 c)

## 5 a)
