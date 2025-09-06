#!/usr/bin/env python
# coding: utf-8

# In[1]:


# let's pull the table from here : https://www.worldometers.info/world-population/population-by-country
from bs4 import BeautifulSoup as bs
import requests as rq
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


url = 'https://www.worldometers.info/world-population/population-by-country'
page = rq.get(url)
page
page.encoding = "utf-8" # to pull the data in the right way as it is on the website 


# In[3]:


page # Response [200], success


# In[4]:


soup = bs(page.text, 'html.parser') # you pull all the text and you want it in an html 
print(soup.prettify()[:1000]) # it's to not show the whole output, it's LONG


# In[7]:


table = soup.find('table', class_ = 'datatable w-full border border-zinc-200') #, class_ ="datatable w-full border border-zinc-200 datatable-table" ) # the information i'm interested in is contained in the table tag of the html
table
print(table.prettify()[:1000])


# In[8]:


columns = table.find_all('th') # find_all outputs a list
col_names = [col.text.strip() for col in columns]
col_names


# In[9]:


table2 = table.find('tbody').find_all('tr') # the tag 'tr' inside the outer tag 'tbody' contains the values of the columns
table2[0]#table 2 is a list (output of find_all)


# In[11]:


table2[0].text.split() #the split was needed because .text was treating everything in 


# In[8]:


# the problem is i'm using 'split()' to split based on the space between the values
 # but for countries like 'united states' it will consider 'united' and 'states' as seperate values
  # so i gotta find a better solution


# In[12]:


# Inside the 'tr' tag which represents an entire row, each individual value has a 'td' tag, so we will exploit that

table3 = table.find_all('td') # this outputs a list

table3[0].text.strip() # the first td tag is for the first row index, to get the whole rows we have to select from 0 to 12 which the number of cols


# In[13]:


# first row: 
[value.text.strip() for value in table3[0:12]]



# In[14]:


# united state row, is the thrid row so from [24:36]

[value.text.strip() for value in table3[24:36]] # awesome


# In[15]:


# let's get all the values as nested list to fit them in a dataframe

values = [row.text.strip() for row in table.find_all('td')] # 1 td tag represent one value, for each value we strip() to remove any unecessary space in both ends of the value

# this get one list containing all the values of the table, in the right way, for example 'united states' isn't split, nice. 


# In[16]:


# let's separate between the rows 
ncol = 12

rows = [values[i : i + ncol] for i in range(0, len(values), ncol)] 
rows[0:2] # now we have each row, this is just a subset


# In[106]:


# Last step : let's create our dataframe, and we will have the same exact table found in the url 

df = pd.DataFrame(data = rows, columns = col_names).set_index('#')


# In[111]:


import os
os.getcwd()


# In[113]:


df.to_csv('Raw_Table_Scraped.csv', index = False)


# In[18]:


df.info()


# In[19]:


pd.set_option('display.max.rows', 240)
df


# # Quick Analysis

# In[77]:


# first we inspect the data, clean it, put the variables in the right format


# In[20]:


df.head() # the column names are a bit inconvenient, as they are hard to write each time especially when you try to plot


# In[21]:


# let's change the col names to better names

df.rename(columns = {'Country (or dependency)': 'country',
                     'Population 2025': 'population',
                     'Yearly Change': 'yearly_change', 
                     'Net Change': 'net_change',
                     'Density (P/Km²)': 'density',
                     'Land Area (Km²)': 'land_area',
                     'Migrants (net)': 'migrants', 
                     'Fert. Rate': 'fert_rate', 
                     'Median Age': 'median_age', 
                     'Urban Pop %': 'urban_pop', 
                     'World Share': 'world share'}, inplace = True)
df.head()


# In[22]:


df.info() # numeric columns aren't numeric so let's convert


# In[23]:


df.isna().sum()


# In[24]:


for col in df.columns.difference(['country']).tolist(): 
    df[col] = df[col].str.strip()
    df[col] = df[col].str.replace('−', '-', regex = False)
    df[col] = df[col].str.replace(',', '')
    df[col] = df[col].str.replace('%', '')
    df[col] = pd.to_numeric(df[col])

df.info() # Now every column has it's right type. 



# In[25]:


df


# In[26]:


df.duplicated().sum() # no duplicates


# In[27]:


df.isna().sum() # only urban pop has some missing values (23), The table for some countries, had empty cells for urban pop, but pandas didn't detect them as NaN because the column was a string, so it considered it as an empty string (""), but when i converted to numeric it detected them.


# ### let's perform some analysis

# ##### countries are already ordered by the number of population, i want to see which continent is the most populated

# In[28]:


# we have to create a continent column, it's easy on python 
import country_converter as coco


# In[29]:


cc = coco.CountryConverter()

df['continent'] = cc.convert(names = df['country'], to = 'continent')
df.head()


# In[30]:


df['continent'].value_counts().sort_values()


# In[31]:


continent_pop = df.groupby('continent')['population'].sum().sort_values(ascending = False) # Asia is the most populated continent
continent_pop = pd.DataFrame(continent_pop)
continent_pop


# In[32]:


ax = sns.barplot(
    data = continent_pop.reset_index(), 
    x = 'population', 
    y = continent_pop.index,
    hue = 'continent',
    palette='crest'
)

plt.title('Total Population by Continent (2025)')
plt.xlabel('Population')
plt.ylabel('Continent')

for i, v in enumerate(continent_pop['population']):
    ax.text(v, i, f"{v:,.0f}", va = 'center', ha = 'left', fontsize=10)

plt.show()

# Asia is approximately 4 times more populated than Africa. 


# In[41]:


continent_pop.plot(
    kind = 'pie', autopct = '%1.1f%%', startangle = 140, cmap = 'Set3', subplots = True
)
plt.ylabel('')
plt.title('Population Distribution by Continent (2025)')
plt.show()

# this is  pretty much self explanatory


# In[33]:


df.groupby('continent')['median_age'].median()


# In[47]:


sns.boxplot(data = df, 
           x = 'continent', 
           y = 'median_age', 
           hue = 'continent')

sns.stripplot(
    data = df,
    x = "continent",
    y = "median_age",
    color = "black",
    size = 3,
    alpha = 0.5
)
plt.title('Median Age Distribution by Continent (2025)')

plt.show()

# There are clear differences in age distributions across continents.

# Africa stands out with a much younger population, with some outliers.

# Europe shows the oldest population structure, highlighting its aging demographics.

# The rest sit in between, but with wider variation across countries.


# In[50]:


plt.figure(figsize=(10,6))

sns.scatterplot(
    data=df,
    x='fert_rate',
    y='median_age',
    hue='continent',
    alpha=0.7,
    s=80,
    edgecolor='w'
)

plt.title('Median Age vs Fertility Rate by Continent (2025)')
plt.xlabel('Fertility Rate (births per woman)')
plt.ylabel('Median Age (years)')
plt.legend(title='Continent')
plt.show()


# Countries with high fertility rate tend to have younger populations, while those with low fertility rate are older. 

  # This clearly shown in this plots for Africa and Europe, Africa countries cluster in the bottom right having high fertility rate resulting in
  # a low median age (Nigeria as an example), while Europe countries cluster in the top left having low fertility rates resulting in a high median age


# In[59]:


top_density = df.sort_values(by = 'density', ascending = False).head(10)
top_density


# In[94]:


plt.figure(figsize=(10,6))
sns.barplot(
    data= top_density,
    x='density',
    y='country',
    palette='magma', 
    hue = 'continent'
)

plt.title('Top 10 Most Densely Populated Countries (2025)')
plt.xlabel('Population Density (people per km²)')
plt.ylabel('Country')

for i, v in enumerate(top_density['density']):
    plt.text(v, i, f"{v:,.0f}", va='center', ha='left')


plt.show()

# This plot was made to see how tightly packed some countries are relative to their land area.

  # It shows places like Monaco and Singapore rank highest, meaning their populations are concentrated in very small spaces.

    # The takeaway is that these countries face pressures compared to large, low-density countries, 

      # density can drive housing and resource challenges.


# In[93]:


top10_net = df.sort_values(by = 'net_change', ascending = False).head(10)

plt.figure(figsize=(10,6))
sns.barplot(
    data = top10_net, 
    x = 'net_change',
    y = 'country',
    hue = 'continent', 
    palette = 'viridis'
)

plt.title('Top 10 Countries by Net Change in Population (2025)')
plt.xlabel('Net Change (People)')
plt.ylabel('Country')

for i, v in enumerate(top10_net['net_change']):
    plt.text(v, i, f"{v:,.0f}", va='center', ha='left')


plt.show()

# The absolute increase or decrease in population (number of people added or lost in a year).
# As expected India and Nigeria are at the top (high fertility rate).


# In[95]:


top10_yearly = df.sort_values(by = 'yearly_change', ascending = False).head(10)

sns.barplot(
    data = top10_yearly, 
    x = 'yearly_change', 
    y = 'country',
    hue = 'continent'
)

plt.title('Top 10 Countries by Yearly Population Growth Rate (2025)')
plt.xlabel('Yearly Change (%)')
plt.ylabel('Country')

for i, v in enumerate(top10_yearly['yearly_change']):
    plt.text(v, i, f"{v:.2f}%", va='center', ha='left')

plt.show()


# In[105]:


df.iloc[230] # Tokelau informations

