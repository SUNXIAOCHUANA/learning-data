# learning-data - class in python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import seaborn as sns
import plotly.offline as py


pd.set_option('precision', 2)
pd.options.display.max_columns = 30
df = pd.read_csv('all_seasons.csv', index_col=0)
country_codes = pd.read_csv("all_seasons.csv", index_col=0)

# Import the data as a DataFrame and check first 5 row
head = df.head()
print(head)
head.to_excel('data1.xls', sheet_name='Sheet1', index=True, engine='xlsxwriter')

# Check data types and if any records are missing
df.info()

describe = df.describe()
print(describe)
describe.to_excel('data2.xls', sheet_name='Sheet2', index=True, engine='xlsxwriter')
categoricals = df.select_dtypes(exclude=[np.number])
cate = categoricals.describe()
print(cate)
cate.to_excel('data3.xls', sheet_name='Sheet3', index=True, engine='xlsxwriter')

# Convert draft_year column into a date type
# Replace Undrafted with NaN
df['drafted'] = np.where(df['draft_year'] != 'Undrafted', 1, 0)
df['draft_year'] = df['draft_year'].replace(r'Undrafted', np.nan, regex=True)

# Convert the column data type to date
df['draft_year'] = pd.to_datetime(df['draft_year'])

# Convert season column to an integer type
df['season'] = pd.to_datetime(df['season'].str[:4])

# Fix country names
df['country'] = df['country'].replace({'Great Britain': 'United Kingdom', 'England': 'United Kingdom', 'Scotland':'United Kingdom',
                                       'Bosnia & Herzegovina': 'Bosnia and Herzegovina', 'Bosnia': 'Bosnia and Herzegovina',
                                       'Cabo Verde': 'Cape Verde', 'St. Vincent & Grenadines': 'Saint Vincent and Grenadines'})
print('Complete')


# Calculate heigh and weight averages
main_variables = df.groupby('player_name', as_index=False).agg({'player_height': 'mean', 'player_weight': 'mean'})
fig = go.Figure(data=go.Scatter(x=main_variables['player_weight'],
                                y=main_variables['player_height'],
                                mode='markers',
                                text=main_variables['player_name'],
                                marker=dict(color='#17408b')
                                ))

fig.update_layout(
    title='NBA Player Height and Weight (for interactive exploration)',
    xaxis_title='Weight (kg)',
    yaxis_title='Height (cm)',
    plot_bgcolor='rgba(0,0,0,0)'
)
py.plot(fig, filename='filename.html')


# Visualise distribution of height and weight data
# Source for average US male heigh: https://en.wikipedia.org/wiki/Average_human_height_by_country
# Source for average US male weight:https://en.wikipedia.org/wiki/Human_body_weight
fig, ax = plt.subplots(1, 2, figsize=(16, 8))
plt.subplots_adjust(wspace=0.05)

sns.distplot(main_variables ['player_height'], ax=ax[0], label='_nolegend_', kde=False)
sns.distplot(main_variables ['player_weight'], ax=ax[1], label='_nolegend_', kde=False)
ax[0].axvline(main_variables ['player_height'].mean(), color='#c9082a', label='NBA Mean')
ax[1].axvline(main_variables ['player_weight'].mean(), color='#c9082a', label='NBA Mean')

# Add lines for average adults to compare
ax[0].axvline(175.3, color='#17408b', label='Average US Male Adult')
ax[1].axvline(88.8, color='#17408b', label='Average US Male Adult')

ax[0].yaxis.set_label_text('Count')
ax[0].xaxis.set_label_text('Height (cm)')
ax[1].xaxis.set_label_text('Weight (kg)')
plt.suptitle('Distribution of Height and Weight Data')
plt.legend(loc='upper right', bbox_to_anchor=(0.98, 1.06), frameon=False)
sns.despine(ax=ax[1], left=True)
sns.despine(ax=ax[0])

plt.show()

plt.figure(figsize=(16, 8))
sns.regplot(x='player_weight', y='player_height', data=main_variables, color='#17408b')
plt.title('Relationship Between Player Height and Weight')
plt.ylabel('Height (cm)')
plt.xlabel('Weight (kg)')
sns.despine()
plt.show()

# print('Correlation between player height and weight is: ' + str(main_variables ['player_height'].corr(main_variables ['player_weight'])))

corr_over_seasons = df.groupby('season')[['player_weight', 'player_height']].corr().unstack().iloc[:, 1]

fig = go.Figure()
fig.add_trace(go.Scatter(x=corr_over_seasons.index,
                         y=corr_over_seasons.values,
                         mode='lines',
                         name='lines',
                         line=dict(color='#17408b')
                         )
              )

fig.update_layout(
    title='NBA Player Height and Weight Correlation Each Season',
    xaxis_title='Season',
    yaxis_title='Correlation',
    plot_bgcolor='rgba(0,0,0,0)'
)
py.plot(fig, filename='filename.html')

fig, ax = plt.subplots(figsize=(16, 8))
ax2 = ax.twinx()

sns.lineplot(x=df['season'], y='player_height', data=df, marker="o", ax=ax, ci=None, label='Height', color='#17408b')
sns.lineplot(x=df['season'], y='player_weight', data=df, marker="o", ax=ax2, ci=None, label='Weight', color='#c9082a')

plt.title('Average Height and Weight Each Season')
ax.xaxis.set_label_text('Season')
ax.yaxis.set_label_text('Height (cm)')
ax2.yaxis.set_label_text('Weight (kg)')

lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc=0)

plt.show()

df['bmi'] = df['player_weight'].values / (df['player_height'].values ** 2) * 10000
plt.figure(figsize=(16, 8))
sns.lineplot(x=df['season'], y='bmi', data=df, marker="o", ci=None, color='#17408b')

plt.title('Average BMI Each Season')
plt.ylabel('BMI')
plt.xlabel('Season')
sns.despine()

plt.show()


# Height and weight based on draft year
first_season_drafted = df.query('season == draft_year')

h_w_by_draft_year = first_season_drafted.groupby('draft_year')['player_height', 'player_weight'].mean()

fig, ax = plt.subplots(figsize=(16, 8))
ax2 = ax.twinx()

sns.lineplot(x=h_w_by_draft_year.index, y='player_height', data=h_w_by_draft_year, marker="o", ax=ax, ci=None, label='Height', color='#17408b')
sns.lineplot(x=h_w_by_draft_year.index, y='player_weight', data=h_w_by_draft_year, marker="o", ax=ax2, ci=None, label='Weight', color='#c9082a')

plt.title('Average Height and Weight of Draft Class')
ax.xaxis.set_label_text('Draft Class')
ax.yaxis.set_label_text('Height (cm)')
ax2.yaxis.set_label_text('Weight (kg)')

lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc=0)

plt.show()


# BMI based on draft year
bmi_draft = h_w_by_draft_year['player_weight'] / (h_w_by_draft_year['player_height'] ** 2) * 10000
bmi_draft = pd.DataFrame(bmi_draft, columns=['bmi'])

plt.figure(figsize=(16, 8))
sns.lineplot(x=bmi_draft.index, y=bmi_draft['bmi'], data=bmi_draft, marker="o", color='#17408b')

plt.title('Average BMI of Draft Class')
plt.ylabel('BMI')
plt.xlabel('Draft Class')
sns.despine()

plt.show()


# Weight and player age
plt.figure(figsize=(16, 8))

w_by_age = df.groupby(['age'])['player_weight'].agg(['mean', 'count'])
w_by_age['outliers'] = np.where(w_by_age['count']<=100, 1, 0)
w_by_age = w_by_age.loc[w_by_age['outliers']==0]

sns.lineplot(x=w_by_age.index, y='mean', data=w_by_age, marker='o', color='#17408b')

plt.title('Average Player Weight for by Age')
plt.ylabel('Average Weight (kg)')
plt.xlabel('Age')
sns.despine()

plt.show()

df_corr = df[df['season'] != '2019-01-01']
df_corr = df[['gp', 'pts', 'reb', 'ast', 'net_rating', 'usg_pct', 'player_weight', 'player_height']]

# Compute the correlation matrix
corr = df_corr.corr()

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr, dtype=np.bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(250, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})

plt.show()

g = sns.PairGrid(df_corr, y_vars=['reb', 'ast'], x_vars=["player_height", "player_weight"], height=3, aspect=2)
g.map(sns.regplot, color='#17408b')
# g.set(ylim=(-1, 11), yticks=[0, 5, 10])
plt.show()

corr_w_r = df.groupby('season')[['player_weight', 'reb']].corr().unstack().iloc[:,1]
corr_w_a = df.groupby('season')[['player_weight', 'ast']].corr().unstack().iloc[:,1]

corr_h_r = df.groupby('season')[['player_height', 'reb']].corr().unstack().iloc[:,1]
corr_h_a = df.groupby('season')[['player_height', 'ast']].corr().unstack().iloc[:,1]

fig = go.Figure()
fig.add_trace(go.Scatter(x=corr_w_r.index, y=corr_w_r.values,
                    mode='lines',
                    name='Weight and Rebounds'))

fig.add_trace(go.Scatter(x=corr_w_a.index, y=corr_w_a.values,
                    mode='lines',
                    name='Weight and Assists'))

fig.add_trace(go.Scatter(x=corr_h_r.index, y=corr_h_r.values,
                    mode='lines',
                    name='Height and Rebounds'))

fig.add_trace(go.Scatter(x=corr_h_a.index, y=corr_h_a.values,
                    mode='lines',
                    name='Height and Assists'))

fig.update_layout(
    title='Correlation Coefficient Comparison Over Time',
    xaxis_title='Season',
    yaxis_title='Coefficient',
    plot_bgcolor='rgba(0,0,0,0)'
)
py.plot(fig, filename='filename.html')

# Largest body weigth transformations

# Compute weight pertentage change values for each player by age
w_pct_change = df.groupby(['season', 'player_name'], as_index=False)['player_weight'].mean().sort_values(['player_name', 'season'])
w_pct_change_values = w_pct_change.groupby(['player_name'])['player_weight'].apply(lambda x: x.pct_change())
w_pct_change = pd.concat([w_pct_change, w_pct_change_values], axis=1).fillna(0)
w_pct_change.columns = ['season', 'player_name', 'weight', 'pct_change']

counts = w_pct_change['player_name'].value_counts()
w_pct_change = w_pct_change[w_pct_change['player_name'].isin(counts.index[counts > 5])]

w_pct_change['sig_cng'] = np.where((w_pct_change.groupby('player_name')['pct_change'].transform('max') > 0.15) | (w_pct_change.groupby('player_name')['pct_change'].transform('min') < -0.15), 1, 0)

a = w_pct_change[w_pct_change['sig_cng'] == 1]
plt.figure(figsize=(16, 8))

sns.lineplot(x="season", y="weight", data=a, units='player_name', estimator=None, hue='player_name')
plt.show()
