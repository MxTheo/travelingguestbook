# Traveling Guestbook
## Empowers people to start conversations

### Description
The aim of this web-application is to facilitate conversation starters with people they do not know, for example people in the train.

It is a web-application where people that received a code on a sociable, can leave a message.

Sociables are the conversation starters.
Sociables are physical items that are passed on from person to person. The physical sociable has a code, that is used to find the page of the sociable. Every time it is passed on, the person who received it leaves a message on the sociable page.
Sociables have goals, which can be a question to answer in a message.

### Domain model
![Entity Relationship Diagram](architecture/domainModel.jpg)

#### Glossary
- **Sociable:** The physical item that is passed on from person to person, which has a code on it
- **Goal:** Every sociable has a goal. The goal answers the question: What does the user wants the receiver to do?
  - The receiver can be asked to answer a question, write in a book, draw in a book. Users can think of goals themselves
- **LogMessage:** The receiver of the sociable leaves a message on the sociable detail page. He can write about his experiences of the conversation, for example.
-  **User:** Users can create sociables and start spreading them around. Messages can be left by anyone with the proper sociable code.

### Contributing
You can fine the contribution guidelines here:
[Contribution guidelines for this project](CONTRIBUTING.md)