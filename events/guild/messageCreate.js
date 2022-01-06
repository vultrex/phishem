const Timeout = new Set(),
    { MessageEmbed, Permissions } = require('discord.js'),
    humanizeDuration = require("humanize-duration"),
    prefix = process.env.prefix,
    Discord = require("discord.js"),
    Schema = require("../../Database/Schema/Guild")
module.exports = async (client , message) => {
    if (message.author.bot) return;
    if (!message.member) message.member = await message.guild.members.fetch(message.member.id);
    if (!message.guild) return;

    const mention = new RegExp(`^<@!?${client.user.id}>`);
/*
    if(mention.test(message.content)) {
        return message.channel.send({
            embeds: [

                new Discord.MessageEmbed()
                    .setColor(2201842)
                    .setAuthor({
                        name: client.user.username,
                        iconURL: client.user.displayAvatarURL({ format: 'png'})
                    })
                    .setDescription("Phishem - Another advanced phish detection bot with YouTube video filtering.\n\nUpon inviting Phishem to your server, auto deletion of of the filters are automatically enabled, but you can enable more functions and configurations with the provided slash commands. \n\n__Slash Information__: \n```bash\n/configure get \"Gets your server's current configurations settings, saying if something is on or off.\"\n\n/search \"Check urls or domains against the phishing databases.\"\n\n/configure bypass \n-----create \"Add links that will be ignored by the filters.\"\n-----remove \"Delete a bypass link which will no longer be ignored.\"\n\n/configure set \n-----delete \"Either enable or disable message deletion upon a positive detection\" \n-----youtube-filter \"Either enable or disable YouTube video filtering for fake nitro generator videos.\"\n-----log \"Set your log channel to get notifications if a phishing or malicious is found.\"\n-----action \"Enable if the bot is either going to ban, kick, or timeout the user when a filter gets triggered.\"\n\n/configure reset \n-----configurations \"Show all the server configurations to reset\"\n---------Delete \"Disables message deletion.\"\n---------YouTube-filter \"Disable YouTube filtering.\" \n---------Log \"Disables logging and delete the logger webhook from the channel.\"\n---------Actions \"Disables all the actions.\"\n---------All \"Disables and resets all the configurations.\" \n```")


            ]
        })
    }

 */
    const youtubeRegex = new RegExp(/(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?/gi)
    Schema.findOne({id: message.guild.id}, async (err, data) => {


    if(new RegExp(/(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]?/gi)) {

        const bitData = await client.phish.bit(message.content)

        if(bitData.match) {
            if (message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR) || message.member.permissions.has(Permissions.FLAGS.MANAGE_GUILD) || message.member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS) || message.member.permissions.has(Permissions.FLAGS.MODERATE_MEMBERS)) return;
            if(data.config.bypass.includes(bitData.matches.map(m => m.domain))) return;

            if(data.config.delete ) {
                if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send({content: "I don't have the permission to delete messages."}).then(m => setTimeout(() => m.delete(), 5000)); else message.delete({reason: "[Automod] Detected a phishing link from the user."})

            }
            if(data.config.action_ban) {
                if(!message.guild.me.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send({content: "I don't have the permission to ban members."}).then(m => setTimeout(() => m.delete(), 5000)); else await message.member.ban({reason: `[Automod] Detected a phishing link from the user.`})

            }
            if(data.config.action_kick) {
                if(!message.guild.me.permissions.has(Permissions.FLAGS.KICK_MEMBERS)) return message.channel.send({content: "I don't have the permission to kick members."}).then(m => setTimeout(() => m.delete(), 5000)); else await message.member.kick({reason: `[Automod] Detected a phishing link from the user.`})

            }
            if(data.config.action_timeout) {
                if(!message.guild.me.permissions.has(Permissions.FLAGS.MODERATE_MEMBERS)) return message.channel.send({content: "I don't have the permission to moderate members."}).then(m => setTimeout(() => m.delete(), 5000)); else message.member.timeout(10000 * 60 * 1000, '[Automod] Detected a phishing link from the user.')

            }

            if(data.log.webhookToken && data.log.webhookID) {

                await client.phish.logger(data.log.webhookID, data.log.webhookToken, message.author, bitData.matches.map(m => m.domain), message.content, message.channel.id, Math.floor(new Date().getTime() / 1000))
            }

        } else if(youtubeRegex.test(message.content) && data.config.youtube_filter) {
            if (message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR) || message.member.permissions.has(Permissions.FLAGS.MANAGE_GUILD) || message.member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS) || message.member.permissions.has(Permissions.FLAGS.MODERATE_MEMBERS)) return;
            const ytLink = new RegExp(/(https?:\/\/[^\s]+)/g)
            if(await client.phish.searchYouTube(message.content.match(ytLink)[0])) {
                if(data.config.bypass.includes(message.content.match(ytLink)[0])) return;
                if(data.config.delete) message.delete({reason: "[Automod] Detected a phishing link from the user."})
                if(data.config.action_timeout) await message.member.timeout(10000 * 60 * 1000, '[Automod] Detected a phishing link from the user.')

                if(data.log.webhookToken && data.log.webhookID) {
                    await client.phish.youtubeLogger(data.log.webhookID, data.log.webhookToken, message.author, message.content.match(ytLink)[0], message.content, message.channel.id, Math.floor(new Date().getTime() / 1000))
                } else return

            } else {
                return
            }

        }
    }
    })

    if (!message.content.toLowerCase().startsWith(prefix)) return;
    const args = message.content.slice(prefix.length).trim().split(/ +/g);
    const cmd = args.shift().toLowerCase();
    if (cmd.length === 0) return;
    const command = client.commands.get(cmd) || client.commands.find((x) => x.aliases && x.aliases.includes(cmd));
    if (command) {
        if (command.timeout) {
            if (Timeout.has(`${message.author.id}${command.name}`)) {
                const embed = new MessageEmbed()
                    .setTitle('You are in timeout!')
                    .setDescription(`:x: You need to wait **${humanizeDuration(command.timeout, { round: true })}** to use command again`)
                    .setColor('#ff0000')
                return message.channel.send({ embeds: [embed] })
            } else {
                command.run(client, message, args);
                Timeout.add(`${message.author.id}${command.name}`)
                setTimeout(() => {
                    Timeout.delete(`${message.author.id}${command.name}`)
                }, command.timeout);
            }
        } else {
            command.run(client, message, args)
        }
    }
}