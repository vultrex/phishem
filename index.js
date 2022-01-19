const { Client, Intents, Collection } = require('discord.js'),
client = new Client({
	disableMentions: "everyone",
	intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES, Intents.FLAGS.GUILD_MEMBERS],
}),
	mongoose = require('mongoose');
require('dotenv').config();

client.phish = require('./Scripts/phish')
client.commands = new Collection();
client.slash = new Collection();
client.aliases = new Collection();
["handlers", "events", "slash"].forEach(handler => {
    require(`./handlers/${handler}`)(client);
});
mongoose.connect(process.env.MONGOSTRING, {useNewUrlParser: true, useUnifiedTopology: true}).then(() => {
	console.log(`[ Database ]`.green + ' Connected to MongoDB')
}).catch((err) => {
	console.log(`[ Database ]`.red + ' Unable to connect to MongoDB Database.\nError: ' + err)
})

require('./slash')(client)
  
client.login(process.env.token);