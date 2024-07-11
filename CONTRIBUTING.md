# Contribution guidelines
## Welcome
You are welcome to contribute to the project. I started this project, while knowing nothing of django and little experience with programming. The main things I wrote in the Definition of Done, I learned more from books, then from experience.There is still much I can learn. I welcome any feedback and would take it into consideration.

### Definition of Done
- Add a docstring
    - Description about the function. Guidelines:
        - "Given input X, calculate/determine/reach output Y, by doing this"
- Write descriptive commit messages
- Write your unit tests before you start coding the logic (TDD principle)
    - Number of UnitTests: Number of if statements + 1
    - 80% Code-Base Coverage
    - Red, Green, Refactor (Test Driven Development)
- Refactor your programs after they work to be more ***readable***. This is when and how program design is learned (Steuben, 2018)<sup>[1](#f1)</sup>
    1. The goal of refactoring is to minimize the time necessary for *others* to understand your code (Steuben, 2018)<sup>[1](#f1)</sup>
    2. "Choose readability over both optimization for speed and optimization for memory use." (Steuben, 2018)<sup>[1](#f1)</sup>
    3. Scout Rule: "Leave the code cleaner then when you found it."
    4. Code review
- Do not start the next function, until you have finished the previous one
    1. Limit your function to do only 1 task
    2. Limit your function to 15 lines
        - People have a working memory of only 4 items (Cowan, 2010)<sup>[2](#f2)</sup>
        - YAGNI Principle
    3. Limit your if statements in a function to 4
    4. Limit the number of parameters to 4
    5. DRY principle
    6. These guidelines come from Visser (2016) <sup>[3](#f3)</sup>
- Stop programming, if you stop understanding what you are doing. Take a walk or a break!
    1. After your break, think of wats to reduce your problem into subproblems, or simplify the *problem*
        - Think about the problem, not the solution
    2. Grab pen and paper, and work it out in your notebook. Plan and think using pen and paper, before you start programming. "Think twice, code once."


### MIT License

Copyright (c) [2024] [Theo Schutte]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.