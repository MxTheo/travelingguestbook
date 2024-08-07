# Traveling Guestbook
## Empowers people to start conversations

### Description
The aim of this web-application is to facilitate conversation starters with people they do not know, for example people in the train.

It is a web-application where people that received a code on a sociable, can leave a message.

Sociables are the conversation starters.
Sociables are physical items that are passed on from person to person. The physical sociable has a code, that is used to find the page of the sociable. Every time it is passed on, the person who received it leaves a message on the sociable page.

### Domain model
![Entity Relationship Diagram](architecture/domainModel.jpg)

#### Glossary
- **Sociable:** The physical item that is passed on from person to person, which has a code on it
- **LogMessage:** The receiver of the sociable leaves a message on the sociable detail page. He can write about his experiences of the conversation, for example.
-  **User:** Users can create sociables and start spreading them around. Messages can be left by anyone with the proper sociable code.

### Contributing
You can fine the contribution guidelines here:
[Contribution guidelines for this project](CONTRIBUTING.md)