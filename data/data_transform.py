import pandas as pd

df = pd.read_csv('data/vitals_time.csv')

# Create a new column 'unstable_in' and set its value to 1 if sbp is below 90, otherwise 0
df['unstable_in'] = (df['sbp'] < 90).astype(int)

# Replace consecutive values of 0 in [unstable_in] with 1 if the number of consecutive 0s is below 2.
count_consecutive_zeros = 0
for i in range(len(df)):
    if df.at[i, 'unstable_in'] == 0:
        count_consecutive_zeros += 1
    else:
        if count_consecutive_zeros < 2:
            df.loc[i - count_consecutive_zeros:i - 1, 'unstable_in'] = 1
        count_consecutive_zeros = 0

# Drop short instability periods below 20 rows
indices_to_drop = []
count_consecutive_ones = 0
for i in range(len(df)):
    if df.at[i, 'unstable_in'] == 1:
        count_consecutive_ones += 1
    else:
        if count_consecutive_ones < 20:
            indices_to_drop.extend(range(i - count_consecutive_ones, i))
        count_consecutive_ones = 0

df = df.drop(index=indices_to_drop)
df = df.reset_index(drop=True)

# Create a new column 'unstable' as a copy of  'unstable_in' 
df['unstable'] = df['unstable_in']

# Shift the 'unstable_in' column by -15 rows to predict instability in future
df['unstable_in'] = df['unstable_in'].shift(-15)

# replace the last 15 missing values with 0
df['unstable_in'] = df['unstable_in'].fillna(0).astype(int)

# Create countdowns for each instability period in [unstable_in]
# Iterate through [unstable_in]. If you encounter a 1, replace it by n = 15 and subsequent values by n = n-1 for n > 0
countdown = 0
for i in range(len(df['unstable_in'])):

    # avoid double alarms in one instability period
    if countdown == 0 and df.at[i, 'unstable_in'] == 1 and df.at[max(i - 2, 0), 'unstable_in'] == 1:
        df.at[i, 'unstable_in'] = 0
        n = 1
        while df.at[i + n, 'unstable_in'] == 1:
            df.at[i + n, 'unstable_in'] = 0
            n += 1

    # start alarm
    elif df.at[i, 'unstable_in'] == 1 and countdown == 0:
        countdown = 15
        df.at[i, 'unstable_in'] = countdown

    # write alarm countdown
    elif countdown > 0:
        countdown -= 1
        df.at[i, 'unstable_in'] = countdown

# drop long phases of stability
# merge unstable_in and unstable
df['tmp'] = df['unstable_in']

for i in range(1, len(df['tmp'])):
    if df.at[i, 'tmp'] == 0:
        df.at[i, 'tmp'] = df.at[i, 'unstable']

# Count the consecutive zeros for each row in the column
consecutive_zeros = df['tmp'].rolling(window=60, min_periods=1).apply(lambda x: (x == 0).sum(), raw=True)

# Find the rows where the consecutive zeros count is 60 or more
rows_to_drop = df[consecutive_zeros >= 60].index

# Remove the rows from the dataframe
df = df.drop(rows_to_drop)
df = df.drop('tmp', axis=1)
df = df.reset_index(drop=True)

# Mark ongoing instability alarm in the countdown coloumn as -1
for i in range(len(df['unstable'])):
    if df.at[i, 'unstable'] == 1:
        df.at[i, 'unstable_in'] = -1

# Save the updated dataframe as a csv file
df.to_csv("data/vitals_time_labled_demo.csv", index=False)