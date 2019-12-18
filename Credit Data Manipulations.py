import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### Data description ###
### Credit loan data set (2000x29)
### Attributes used: Current unpaid balance, Loan to Value ratio, FICO score, Loan number, Loan date

# Read in whole workbook (Note: dummy file path and name)
xlsx = pd.ExcelFile('/file/path/multi-sheet-workbook.xlsx')

# Capture the 'Data' sheet
df = xlsx.parse('Data')

# Change CURRENT_BALANCE data type to float to get decimal output from mean()
df['CURRENT_BALANCE'] = df['CURRENT_BALANCE'].astype('float64')

# Set display options for print statements
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)



### --------------- REPORT 1: Data by Lender Institution Type --------------- ###
### Group by type of lender institution
### Find loan count, mean and max/min current unpaid balances by lender type

# Use agg() to calculate
df_by_lender_type = df.groupby('LENDER_INST_TYPE_DESCRIPTION').agg(
	{
	'LOAN_NUMBER': [('LOAN_COUNT', 'count')],
	'CURRENT_BALANCE': [('MEAN_CURRENT_BALANCE', 'mean'), ('MAX_CURRENT_BALANCE', max), ('MIN_CURRENT_BALANCE', min)]
	})

### --------------- REPORT 2: Data by LTV (Loan to Value) Cohorts --------------- ###
### Split dataframe into Loan to Value (LTV) cohorts/bins
### Find loan count, mean and max/min current unpaid balances by LTV cohort

# Designate ranges for LTV cohorts/bins
LTV_ranges = [0,85,90,95,float('inf')]

# Cut dataframe by LTV and group by cuts to create bins 
# Note: 'include_lowest=True' seems to fudge the lowest value down 0.001 instead of changing the interval bracket
LTV_bins = df.groupby(pd.cut(df['LTV'], LTV_ranges, right=True, include_lowest=True))

# Number of loans in each LTV bin
LTV_counts = LTV_bins.count()

# Mean, max/min current balances by LTV
LTV_means = LTV_bins.CURRENT_BALANCE.mean()
LTV_max_balances = LTV_bins.CURRENT_BALANCE.max()
LTV_min_balances = LTV_bins.CURRENT_BALANCE.min()



### --------------- REPORT 3: Data by Loan Age Cohort  --------------- ###
### Split dataframe into loan age (by months) cohorts/bins
### Find loan count, mean and max/min current unpaid balances by loan age cohort

# Subtract LOAN_ORIG_DATE from 6/1/13 (START_DATE) to create LOAN_AGE attribute
df['LOAN_AGE'] = pd.to_datetime(df['START_DATE']) - df['LOAN_ORIG_DATE']

# Convert LOAN_AGE to months
df['LOAN_AGE'] = df['LOAN_AGE']/np.timedelta64(1, 'M')

# Designate ranges for ranges of months
loan_age_ranges = [0,10,20,30,40,float("inf")]

# Cut dataframe by LOAN_AGE and group by cuts to create bins
loan_age_bins = df.groupby(pd.cut(df['LOAN_AGE'], loan_age_ranges, right=False))

# Number of loans in each bin
loan_ages = loan_age_bins.count()

# Mean, max/min current unpaid balance in each bin
loan_age_mean_balances = loan_age_bins.CURRENT_BALANCE.mean()
loan_age_max_balances = loan_age_bins.CURRENT_BALANCE.max()
loan_age_min_balances = loan_age_bins.CURRENT_BALANCE.min()

# Create separate bin for loans of unknown age
loans_unknown_age = df[df['LOAN_ORIG_DATE'].isnull()]

# Number loans of unknown age
unknown_age_count = loans_unknown_age['LOAN_NUMBER'].count()

# Mean, max/min current balances 
unknown_age_mean_balance = loans_unknown_age['CURRENT_BALANCE'].mean()
unknown_age_max_balance = loans_unknown_age['CURRENT_BALANCE'].max()
unknown_age_min_balance = loans_unknown_age['CURRENT_BALANCE'].min()


### --------------- REPORT 4: Total CURRENT_BALANCE by LTV Cohorts and FICO Cohorts ------------- ###
### Split data frame into FICO cohorts
### Create cross-tabulation/contingency table of sum of current unpaid balance by LTV and FICO cohorts

# Designate ranges for FICO cohorts/bins
FICO_ranges = [0,600,700,800,float("inf")]

# Cut dataframe by FICO score
df["FICO_BIN"] = pd.cut(df['FICO_SCORE'], FICO_ranges, right=False)

# Cut dataframe by LTV
df["LTV_BIN"] = pd.cut(df['LTV'], LTV_ranges, right=True, include_lowest=True)

# Create crosstabulation with rows=FICO and cols=LTV
ct = pd.crosstab(df.FICO_BIN, df.LTV_BIN, values=df.CURRENT_BALANCE/100000000, aggfunc=sum,
	rownames=['FICO Score Range'], colnames=['Loan to Value Range'])

# Create grouped bar graph of crosstab results
ct.plot(kind='bar')
plt.title('Total Unpaid Balance by LTV Cohorts and FICO Cohorts', fontsize=14)
plt.xlabel('FICO Cohorts', fontsize=12)
plt.xticks(rotation=30)
plt.ylabel('Unpaid Balance (in 100s of millions)', fontsize=12)
plt.style.use('grayscale')
plt.show()

