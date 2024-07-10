# Traveling Guestbook
## Empowers people to start conversations
### Description
The aim of this web-application is to facilitate conversation starters with people they do not know, for example people in the train.

It is a web-application where people that received a code on a sociable, can leave a message.

Sociables are the conversation starters.
Sociables are physical items that are passed on from person to person. The physical sociable has a code, that is used to find the page of the sociable. Every time it is passed on, the person who received it leaves a message on the sociable page.
Sociables have goals, which can be a question to answer in a message.

### Domain model
![Entity Relationship Diagram]
(architecture/domainModel.jpg)

### Definition of Done
- Add a docstring
    - Description about the function. Guidelines:
        - "Given input X, calculate/determine/reach output Y, by doing this"
- Write descriptive commit messages
- Write your unit tests before you start coding the logic (TDD principle)
    - Number of UnitTests: Number of if statements + 1
    - 80% Code-Bse Coverage
    - Red, Green, Refactor (Test Driven Development)
- Refactor your programs after they work to be more ** *readable***. This is when and how program design is learned (Steuben, 2018)[^1]
    1. The goal of refactoring is to minimize the time necessary for *others* to understand your code (Steuben, 2018)[^1]
    2. > Choose readability over both optimization for speed and optimization for memory use. (Steuben, 2018)[^1]
    3. Scout Rule: "Leave the code cleaner then when you found it."
    4. Code review
- Do not start the next function, until you have finished the previous one
    1. Limit your function to do only 1 task
    2. Limit your function to 15 lines
        - People have a working memory of only 4 items (Cowan, 2010)[^2]
        - YAGNI Principle
    3. Limit your if statements in a function to 4
    4. Limit the number of parameters to 4
    5. DRY principle
    6. These guidelines come from Visser, 2016[^3]
- Stop programming, if you stop understanding what you are doing. Take a walk or a break!
    1. After your break, think of wats to reduce your problem into subproblems, or simplify the *problem*
        - Think about the problem, not the solution
    2. Grab pen and paper, and work it out in your notebook. Plan and think using pen and paper, before you start programming. "Think twice, code once."


[^1]Stueben, M. (2018). Good Habits for Great Coding. In Apress eBooks
[^2]Cowan, N. (2010). The Magical Mystery Four. Current Directions in Psychological Science, 19(1), 51–57
[^3]Visser, J., Rigal, S., Van Der Leek, R., Van Eck, P., & Wijnholds, G. (2016). Building Maintainable Software, Java Edition: Ten Guidelines for Future-Proof Code. “O’Reilly Media, Inc.”