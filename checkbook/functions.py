# import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def sep_trans(f_df):
    # take the original checkbook dataframe and returns two dataframs, separating credits from debits
    
    # Create and clean up creditor df
    cred_df = f_df.query('Credit > 0')
    cred_df = cred_df[['Check #', 'Date', 'Transaction Description', 'Credit']]
    cred_df.rename(columns={'Credit':'Amount'}, inplace=True)
    
    # Create and clean up payee df
    pay_df = f_df.query('Payment > 0')
    pay_df = pay_df[['Check #', 'Date', 'Transaction Description', 'Payment']]
    pay_df.rename(columns={'Payment':'Amount'}, inplace=True)

    # Return values
    return cred_df, pay_df

def summary(f_df):
    # takes a sep_trans() generated dataframe and combines creditors/payees to unique buckets
    
    sum_df = f_df.groupby('Transaction Description').agg(
        num_tran=('Amount', 'count'),
        total_amt=('Amount', 'sum'))
    
    # Add a column containing average transaction amt round 2 decimal
    sum_df['avg_tran'] = round((sum_df['total_amt'] / sum_df['num_tran']),2)
    
    # Sort sum_df by 'num_trans' in descending order
    sum_df = sum_df.sort_values(by=['total_amt', 'num_tran'], ascending=False)
    
    # Reset indexing of sum_df and return
    sum_df = sum_df.reset_index()
    return sum_df

def pie_chart(df, agg_threshold, explode_threshold, title):
    # takes dataframe created by the summary() function and returns a pie chart object
    
    # create local copy of df
    f_df = df.copy()
    
    # create column with percentage value of each entry
    total = f_df['total_amt'].sum()
    f_df['percentage'] = (f_df['total_amt'] / total) * 100
    
    # create aggregated dataframe with transactions below threshold percentage
    agg_df = f_df[f_df['percentage'] < agg_threshold]
    combined_row = {
        'Transaction Description': f'Combined trans < {agg_threshold} %',
        'num_tran': agg_df['num_tran'].sum(),
        'total_amt': agg_df['total_amt'].sum(),
        'avg_tran': round((agg_df['total_amt'].sum()) / (agg_df['num_tran'].sum()),2),
        'percentage': agg_df['percentage'].sum()        
    }
    
    # delete rows from f_df that were captured in the agg_df
    f_df = f_df[f_df['percentage'] > agg_threshold]
    
    # combine the aggregated transactions with newly edited f_df
    combined_df = pd.concat([f_df, pd.DataFrame([combined_row])], ignore_index=True)
    
    # get variables from df for chart
    sizes = combined_df['percentage']
    labels = combined_df['Transaction Description']

    # create list with explode values
    explode = [0 if percentage < explode_threshold else .1 for percentage in combined_df['percentage']]  
    
    # create and return chart
    plt.figure(figsize=(8,8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, explode=explode)
    plt.title(title)
    plt.axis('equal')
    return plt

def histogram(i_df, o_df, n):
    # takes creditor (i_df) and payee (o_df) dataframes and returns histogram
    # n represents number of months covered by data - histogram is partitioned by month, quarter or year based on this

    if n < 36:
        # create month_year column in each of the dataframes
        i_df['month_year'] = i_df['Date'].dt.to_period('M')
        o_df['month_year'] = o_df['Date'].dt.to_period('M')
        # calculate monthly amounts for each of the dataframes
        i_grouped = i_df.groupby(['month_year'])['Amount'].sum()
        o_grouped = o_df.groupby(['month_year'])['Amount'].sum()
        time = 'Month'
    elif n < 144:
        # create quarter_year column in each of the dataframes
        i_df['quarter_year'] = i_df['Date'].dt.to_period('Q')
        o_df['quarter_year'] = o_df['Date'].dt.to_period('Q')
        #calculate quarterly amounts for each of the dataframes
        i_grouped = i_df.groupby(['quarter_year'])['Amount'].sum()
        o_grouped = o_df.groupby(['quarter_year'])['Amount'].sum()
        time = 'Quarter'
    else:
        # create year_year column in each of the dataframes
        i_df['year_year'] = i_df['Date'].dt.to_period('Y')
        o_df['year_year'] = i_df['Date'].dt.to_period('Y')
        # calculate yearly amounts for each of the dataframes
        i_grouped = i_df.groupby(['year_year'])['Amount'].sum()
        o_grouped = o_df.groupby(['year_year'])['Amoung'].sum()
        time = 'Year'
    

    # plot histogram
    plt.figure(figsize=(10,6))
    plt.bar(i_grouped.index.astype(str), i_grouped, color='green', alpha=0.7, label='Inflows')
    plt.bar(o_grouped.index.astype(str), o_grouped, color='red',alpha=0.7, label='Outflows')
    plt.title(f'Transactions by {time} and Type')
    plt.xlabel(time)
    plt.ylabel('Amount')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def line_graph(sum_df, tran_df, lines, remove_transfer):
    # create line_graph using summary datafram, transaction dataframe for lines number of transaction descriptions removing 'transfer' transactions if requested
    
    # if remove_transfer value is True, remove 'transfer' transactions and take top 'lines' of the sum_df dataframe into top_payee_df - otherwise just take top lines
    if remove_transfer:
        top_payee_df = sum_df[~sum_df['Transaction Description'].str.contains('transfer', case=False)]

    # print(sum_df[sum_df['Transaction Description'].str.contains('transfer', case=False)])
    
    # limit number of payees to lines variable    
    top_payee_df = top_payee_df.head(lines)

    # creat column in tran_df that contains month-year of transactions
    tran_df['month-year'] = tran_df['Date'].dt.to_period('M')

    # merge dataframes and drop unneeded columns
    merged_df = pd.merge(top_payee_df, tran_df, on='Transaction Description')
    merged_df = merged_df[['Transaction Description', 'month-year', 'Amount']]

    # group by date and description, sum transaction amount
    grouped_df = merged_df.groupby(['month-year', 'Transaction Description']).sum().reset_index()

    # create pivoted df to have 'Transaction Description' as columns
    pivot_df = grouped_df.pivot(index='month-year', columns='Transaction Description', values='Amount').fillna(0)

    # create line graph
    pivot_df.plot(kind='line', marker='o', figsize=(10,6))
    plt.title('Transactions by Payee')
    plt.xlabel('Date')
    plt.ylabel('Transaction Amount')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend(title='Payee')
    plt.tight_layout()
    return plt
    








    