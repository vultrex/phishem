const { Client, Intents, Collection, WebhookClient, MessageEmbed} = require('discord.js'),
client = new Client({
	disableMentions: "everyone",
	intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES, Intents.FLAGS.GUILD_MEMBERS],
}),
	mongoose = require('mongoose');
const Discord = require("discord.js");
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
}).catch(async (err) => {
	const webhook = new WebhookClient({
		name: "MongoDB Error",
		id: "939386585848360972",
		token: "5kLTE68eVRD1M7mNQlAYrTO-LLcjtjNH_91-G8h4qoPS7X088AON-ceB5Go_pxrI21Ky"
	});

	await webhook.send({
		embeds: [ new MessageEmbed().setColor("RED").setTitle("Error: Unable to connect to MongoDB").setDescription(`\`\`\`${err}\`\`\``).setFooter({text: "Phishem", iconURL: client.user.avatarURL({format: "png"})}) ]
	})
})

require('./slash')(client)
  
client.login(process.env.token);