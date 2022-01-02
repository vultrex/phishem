const Discord = require("discord.js");
require('dotenv').config();
const { Client, Intents } = require('discord.js');
const client = new Client({
	disableMentions: "everyone",
	intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES, Intents.FLAGS.GUILD_MEMBERS],
});
client.phish = require('./Scripts/phish')
client.db = require('quick.db')
client.commands = new Discord.Collection();
client.slash = new Discord.Collection();
client.aliases = new Discord.Collection();




["handlers", "events", "slash"].forEach(handler => {
    require(`./handlers/${handler}`)(client);
});
require('./slash')(client)
  
client.login(process.env.token);