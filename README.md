# Bedank voor het contact (before Traveling Guestbook)
# [bedanktvoorhetcontact.nl](www.bedanktvoorhetcontact.nl)
## Social media for real-life interactions

### Description
The aim of this web-application is to facilitate interaction between you and strangers, for example people in the train. You can end the conversation by handing out a thank you.

It is a web-application where people that received a code, can read the message left for them. They can also leave a message themselves.

There are the conversation enders. You can end a conversation by thanking the other person with a code. The hope is that others will also thank others with the same code. In that way, the physical item is passed on from person to person.
The code is used to find the page where all the messages are left. Every time it is passed on, the person who gave it leaves a chatmessage to the receiver.

For more Dutch information about how the application works, see [help](https://bedanktvoorhetcontact.nl/help).

### Language
The Web-Application is in Dutch. The code and back-end is in English.

### Domain model
![Entity Relationship Diagram](architecture/domainModel.jpg)

#### Glossary
-  **User:** Users can create codes and start spreading them around. Messages can be left by anyone who have a code. You do not need an account for that.
- **ChatRoom:** The code can be written on some physical thing. This physical item is used to thank the other for the conversation. Hopefully that other will also thank others with the same code for the conversation. (Have not renamed it yet in the backend)
- **ChatMessage:** With the code, the giver leaves a message on the specific page for the receiver of the code to read. He can write about his experiences of the conversation.

#### Flowchart for getting to the chat
![Flowchart to chatroom detail](architecture/flowToChatRoomDetail.png)
Most important functionality is to find the message left for them.

### Contributing
You can fine the contribution guidelines here:
[Contribution guidelines for this project](CONTRIBUTING.md)