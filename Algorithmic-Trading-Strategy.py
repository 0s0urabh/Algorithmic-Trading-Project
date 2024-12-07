# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ================================================
# Step 1: Load and Preprocess the Data
# ================================================

# Load the dataset
df = pd.read_csv('FINAL_PREPARED_MARKET_DATA.csv')

# Convert 'Date' and 'Time' columns into a single datetime index
# This allows for easy time-series analysis
df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'].str.split(' - ').str[0])
df.set_index('Datetime', inplace=True)

# Add a percentage change column to calculate returns
df['Returns'] = df['Intraday Price'].pct_change()

# ================================================
# Step 2: Define the Trading Strategy
# ================================================

# Define trading windows
trading_windows = {
    'night': ('03:00', '05:00'),
    'morning': ('04:00', '07:00'),
    'evening': ('18:00', '19:00'),
    'peak_volatility': ('20:00', '21:00')
}

# Initialize backtesting parameters
capital = 100000  # Starting capital in currency
position = 0      # Position size (units of the asset)
transaction_cost = 0.001  # 0.1% transaction cost
starting_capital = capital  # Save starting capital for calculations

# ================================================
# Step 3: Backtesting Logic
# ================================================

# Iterate through each row in the DataFrame to simulate trades
for i in range(1, len(df)):
    # Get the current time of the trading session
    current_time = df.index[i].time()

    # Night trading logic
    if trading_windows['night'][0] <= current_time.strftime('%H:%M') <= trading_windows['night'][1]:
        if position == 0:  # Enter position
            position = capital / df['Intraday Price'].iloc[i]
            capital -= position * df['Intraday Price'].iloc[i] * (1 + transaction_cost)

    # Morning trading logic
    elif trading_windows['morning'][0] <= current_time.strftime('%H:%M') <= trading_windows['morning'][1]:
        if position > 0:  # Exit position
            capital += position * df['Intraday Price'].iloc[i] * (1 - transaction_cost)
            position = 0

    # Evening trading logic
    elif trading_windows['evening'][0] <= current_time.strftime('%H:%M') <= trading_windows['evening'][1]:
        if position == 0:  # Enter position
            position = capital / df['Intraday Price'].iloc[i]
            capital -= position * df['Intraday Price'].iloc[i] * (1 + transaction_cost)

    # Peak volatility trading logic
    elif trading_windows['peak_volatility'][0] <= current_time.strftime('%H:%M') <= trading_windows['peak_volatility'][1]:
        if position > 0:  # Exit position
            capital += position * df['Intraday Price'].iloc[i] * (1 - transaction_cost)
            position = 0

# Calculate net profit and Sharpe Ratio
net_profit = capital - starting_capital
returns = df['Returns'].dropna()
sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252 * 48)  # 252 trading days, 48 half-hour periods

# Print summary statistics
print("Net Profit:", net_profit)
print("Sharpe Ratio:", sharpe_ratio)

# ================================================
# Step 4: Visualization of Results
# ================================================

# Plot intraday price and day-ahead price with trading windows
plt.figure(figsize=(15, 8))
plt.plot(df.index, df['Intraday Price'], label='Intraday Price')
plt.plot(df.index, df['Day Ahead Price'], label='Day Ahead Price', alpha=0.7)

# Highlight trading windows
for date in df.index.date:
    plt.axvspan(pd.Timestamp(date).replace(hour=3), pd.Timestamp(date).replace(hour=5), alpha=0.2, color='blue', label='Night Trading' if date == df.index.date[0] else '')
    plt.axvspan(pd.Timestamp(date).replace(hour=4), pd.Timestamp(date).replace(hour=7), alpha=0.2, color='green', label='Morning Trading' if date == df.index.date[0] else '')
    plt.axvspan(pd.Timestamp(date).replace(hour=18), pd.Timestamp(date).replace(hour=19), alpha=0.2, color='red', label='Evening Trading' if date == df.index.date[0] else '')

plt.title('Intraday Price and Trading Windows')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ================================================
# Step 5: Analyze Volatility and Daily Statistics
# ================================================

# Calculate rolling volatility
df['Volatility'] = df['Returns'].rolling(window=48).std() * np.sqrt(48)

# Plot volatility
plt.figure(figsize=(15, 6))
plt.plot(df.index, df['Volatility'], label='Volatility')
plt.title('Rolling Volatility')
plt.xlabel('Date')
plt.ylabel('Volatility')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Compute daily statistics
daily_stats = pd.DataFrame({
    'Mean_Intraday': df['Intraday Price'].resample('D').mean(),
    'Mean_DayAhead': df['Day Ahead Price'].resample('D').mean(),
    'Volatility': df['Intraday Price'].resample('D').std()
})

# Display daily statistics
print("Daily Statistics:")
print(daily_stats)

# Plot daily statistics
plt.figure(figsize=(15, 6))
daily_stats['Mean_Intraday'].plot(label='Mean Intraday Price', alpha=0.8)
daily_stats['Mean_DayAhead'].plot(label='Mean Day Ahead Price', alpha=0.8)
daily_stats['Volatility'].plot(label='Daily Volatility', alpha=0.8)
plt.title('Daily Market Statistics')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
