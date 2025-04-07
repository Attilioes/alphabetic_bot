my first actual telegram bot detects in a group chat when a message has its words in alphabetical order. 
please note it's a just-for-fun thing 
token is scraped off bc it's my bot, but feel free to entirely copy and paste the code into a bot of your own.
massive help of chat gpt to set the bot structure up so if you're reading this, chances are you won't even need it to replicate this thing from scratch.
json structure to store the hit count and the max length detected for each group it's been used in.
minimum length 4 otherwise there would be too many irrelevant hits
idk how it could work with other languages, in Italian 4 seems a fair threshold. 
command /count to have the bot tell the hit count of the group, /longest to have it tell the max length detected in the group.
the json file is to give an idea of how it stores data in a dictionary structure.
