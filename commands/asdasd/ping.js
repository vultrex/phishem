const Discord = require('discord.js')

module.exports = {
    name: "ping",
    description: "Get bot speed",
    timeout: 5000,
    run: async(client, message) => {
        message.channel.send({content: `Pong! ${client.ws.ping}ms`})
    }
}