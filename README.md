# personal_budget_planner
Personal Budget Planner
# <span style="color:purple">  PERSONAL BUDGET PLANNER</span>

### Video Demo:  <URL HERE>
### Description:

**Personal Budget Planner** is an easy-to-use web application that helps to plan your household budget. It allows to manage your money better and control your bills. You can spot areas where you can spend less and start saving.
Once a user is registered, they provide the following data:
- name of budget
- projected and actual income categories (salary, allowances, dividends, others)
- projected and actual expense categories (groceries, health, clothing, fuel and car maintenance, entertainment, home supplies, electricity, gas, water, internet, telephone, other).
Then, the data is submitted and a user can see the budget summary. The following items are displayed:
- calculated total income and expenses
- balance and appropriate alert depending on positive or negative outcome
- the spending with max value
- breakdown of all expense categories.

The user can see how much they earned and how much they spent. The calculated balance shows if you earn more than you spend or you spend more than you earn. The summary provides you with personalized alert and the highest expense category. You can analyse your spending categories by means of a pie chart. The data is saved and and you can see your previous budgets in a brief form anytime you like. The Personal Budget Planner encourages users to read and follow the tips **‘How to budget smartly’**.


**app.py**

First, Flask is configured then,  Flask is configured to store sessions. The connection is set with database.db. And the file disables caching of responses.

**helpers.py**

There, you’ll find an apology function and login_required function.

**static/**

The folder contains css file and pictures used in the app.
**templates/**

The folder contains all html templates. The layout template arranges general layout of other templates. It includes stylesheet and Bootstrap links. Displays user menu depending on whether a user is logged in or logged out.

**The app.py includes the following routes:**

**register**

A user submits a form via POST. If a user fails to provide name, password, their name is already taken or repeated password is different, an apology is rendered. If a user succeeds, the data (name and password) are sent to the database. The password is hashed. Then, a flash message appears: *"Registered!"*


**login**

A user submits their username and password. App.py checks if the data is in the database. If it fails or a user does not provide data, apology function is called. If it succeeds, app remembers which user has logged in by means of session.

**logout**

It clears session and a user is logged out.

**index**

It renders index.html that is a brief manual how to use PBP.

**budget_history**

It displays an HTML form which allows to choose the history budget. A user chooses the budget name and it redirects to the report_budget template. If a user does not have any budget yet, a flash message is displayed *"It seems you have no budget history yet."*

**report_budget**

Depending on which budget name a user selected, a query is sent to the database and all the budget items are displayed (income and expenses, total income and total expenses etc.)
Depending on balance result (positive, negative or null), a user can see a personalized alert. Then, again a database query is sent to append actual expense values and the app.py looks for their max value. A user can see which spending is the highest.

**tips**

Here, a user can read practical tips **'How to budget smartly’**.

**getstarted**

A user fills in a form and submits via POST a budget name and all income and expenses categories. Then they are redirected to the summary template.

**summary**

It sends a query to the database, append income and expense data into a dict. Total income, total expenses and balance are calculated. Depending on balance result (positive, negative or null), a user can see a personalized alert. Then, again a database query is sent to append actual expense values and the app.py looks for their max value. A user can see which spending is the highest. There’s a breakdown of all expense categories as a pie chart.

**pie_plot**

A [Matplotlib](https://matplotlib.org/) framework is used to plot a pie chart. The expenses values are appended from the database to a list and then the chart is rendered displaying spending categories and their percentage values.

