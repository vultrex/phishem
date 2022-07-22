# Phishem
Phishem is a bot made to combat against phishing or malicous websites being sent on [discord](https://discord.com).

Bot invite: [Invite](https://discord.com/oauth2/authorize?client_id=926687914174341130&scope=bot+applications.commands&permissions=1377342712950)

## How to host locally
1) Create a file named `.env` in the root directory of the project. Inside the file fill out the following details:]
```
TOKEN=""
MONGOSTRING="" (MongoDB connection string)
PREFIX="+"
CLIENTID = "" (Bot client ID)
DEVELOPERS=[] (Array of developers IDs)
LOGHOOK="" (Log webhook url)
```
2) Run `npm install`
3) Run `npm run dev` or `node .`
