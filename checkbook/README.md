# CHECKBOOK ANALYSIS
#### Project Overview:
This project provides a comprehensive analysis of a simple checkbook ledger in MS Excel using the Jupyter Lab environment. By using data visualization techniques, a detailed examination of deposits and payments across all parties is presented, providing a clear understanding of historical financial transactions.
### Files Included
- **Checkbook.xlsx** - This is a simple checkbook ledger in MS Excel format.  Briefly, the columns are as follows:
    * A - Check # - Field to enter check number or specify the type of payment or depost
    * B - Date - Date of transaction in mm/dd/yy format
    * C - Transaction Description - for the sake of accurate analysis, it is best to be consistent in the naming of recurring transactions.
    * D - Payment amount (left blank if a credit)
    * E - 'ty' column - if blank, indicates that transaction has not yet cleared in the checking account.  User should balance the ledger with the statement by entering 'X' in this column when transaction has cleared.
    * F - Credit amount (left blank if a debit)
    * G - Balance - Current balance is caculated once other fields are entered.

    **Other notable fields:**

    * B1 - Amount 'out' - or total of transactions that have not yet been denoted as 'cleared' by column E - calculated by subtracting total amount uncleared debits from total amount of uncleared credits.
    *D1 - Current balance as denoted by latest bank statement - should not reflect amount out (B1)
    * F1 - Currrent balance calculated by adding the amount out (column B) to the current statement balance (column D).
    * G1 - Current balance between bank statement and spreadsheet ledger - this is calculated by subtracting the last value in column G from cell F1.  If the checkbook ledger and the bank statement are in balance, this number will be zero.  If not zero, the amount discrepent needs to be reconciled between the two.
- **checkbook_2.ipynb** - This is the Jupyter Lab file that extracts and analyzes data from Checkbook.xlsx
    Briefly, sections are as follows:
    * [1] - import modules
    * [2] - set default start and end date for data analysis - end date is set in the future in caste post dated transactions are included.
    * [3] - set default aggregating thresholds for pie charts.  This is necessary to group smaller incidental transactions that you may not want to graph.  Allows for better representation of larger / recurring transactions.  Values are set to percentage.  Default payees for line graph is set here as well.
    * [4] - [7] - import and inspect data from Checkbook.xlsx
    * [8] - [11] - call sep_trans() function to separate data into creditor and payee dataframes
    * [12] - call summary() function to summarize both the creditor and payee data
    * [13] - [14] - call pie_chart() function to create pie charts for creditors and payees
    * [15] - calls histogram() function after calculating number of months to display a combined histogram of inflows and outflows
    * [16] - calls line_graph() function to display line graph of top outflows by payee
- **functions.py** - This file contains functions that sort and clean data as well as create and return graphs.
    - **def sep_trans(f_df)** - accepts a dataframe as input and separates credits from debits, does some clean up and returns separate dataframs for each
    - **def summary(f_df)** - takes a dataframe created by sep_trans() and groups transactions to unique payees or creditors using the 'Transaction Description' field - returned dataframes are used subsequently for graphing
    - **def pie_chart(df, agg_threshold, explode_threshold, title)** - takes a dataframe created by the summary() function (df) and returns a formatted pie chart.  Variable agg_threshold and explode_threshold were defined early in checkbook_2.ipnyb file.  Additionally, the title for the chart is taken as an argument.
    - **def histogram(i_df, o_df, n)** - takes  creditor (i_df) and payee (o_df) datframes created by summary() function and returns a formatted histogram.  Function will partition the histogram by time period depending on the number of months (n) specified to the function to esure readability of the graph.
    - **def line_graph(sum_df, tran_df, lines, remove_transfer)** - function creates and returns line graph of top payees over time.  Requires sum_df and tran_df created above, in addition to the number of payees to be included (lines).  A boolean value is used to delete 'transfer' type transactions, as these may not be true expenses and probably want to be excluded from this chart (defaults to true).  Could be modified to provide graph for creditors.


