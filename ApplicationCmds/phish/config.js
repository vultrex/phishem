const { MessageEmbed } = require('discord.js');

module.exports = {
    name: "config",
    description: "Set the configuration for your server",
    options: [
        {
            name: "get",
            description: "Get the current configuration",
            type: 1,
        },
        {
            name: "create",
            description: "Set configuration for your server",
            type: 1,
            options: [
                {
                    name: "delete",
                    description: "If the detected phishing links should be deleted.",
                    type: 5,
                },
                {
                    name: "log",
                    description: "The channel I should send log detections in.",
                    type: 	7,
                },
                {
                    name: "action",
                    description: "The action to take when a phishing or malicious link is detected.",
                    type: 3,
                    choices: [
                        {
                            name: "Ban",
                            value: "ban"
                        },
                        {
                            name: "Kick",
                            value: "kick"
                        },
                        {
                            name: "Timeout",
                            value: "timeout"
                        }
                    ]
                },
            ]

        },
        {
            name: "reset",
            description: "Reset the server configurations back to it's original state.",
            type: 1,
            options: [
                {
                    name: "reset",
                    description: "Reset the server configurations back to it's original state.",
                    type: 3,
                    choices: [
                        {
                            name: "Delete",
                            value: "delete"
                        },
                        {
                            name: "Log",
                            value: "log"
                        },
                        {
                            name: "Action",
                            value: "action"
                        },
                        {
                            name: "All",
                            value: "all"
                        }
                    ]
                },
            ]
        },
    ],
    category: "phish",
    run: async(interaction,  client) => {
        if(interaction.options._subcommand === "get") {
            let configEmbed = new MessageEmbed()
                .setTitle(`The current configuration for \`${interaction.guild.name}\``)
                .setColor(0x00AE86)
                .setDescription(`\`\`\`diff\n${await client.db.fetch(`${interaction.guild.id}.config.delete`) ? "+" : "-"} Delete Links: ${await client.db.fetch(`${interaction.guild.id}.config.delete`) ? "On" : "Off"}\n${await client.db.fetch(`${interaction.guild.id}.config.log.id`) ? "+" : "-"} Logging: ${await client.db.fetch(`${interaction.guild.id}.config.log.id`) ? "On" : "Off"}\`\`\``)
            interaction.reply({embeds: [configEmbed]});
        }
        const value = interaction.options._hoistedOptions
        if(value[0]) {
            if(!value[0]) return interaction.reply({content: "<:3595failed:926715200172867624> You must specify a option!", ephemeral: true})
            if(value.length > 1) return interaction.reply({content: "<:3595failed:926715200172867624> You can only specify one option!", ephemeral: true})
            switch(interaction.options._hoistedOptions[0].name) {

                case "delete":
                    if(await client.db.fetch(`${interaction.guild.id}.config.delete`)) return interaction.reply({content: "<:3595failed:926715200172867624> Phishing links are already being deleted!", ephemeral: true})
                    client.db.set(`${interaction.guild.id}.config.delete`, interaction.options._hoistedOptions[0].value)
                    interaction.reply({content: "<:9294passed:926715199950561341> The detected phishing or malicious links will now be deleted.", ephemeral: true})
                    break
                case "action":

                    switch(value[0].value) {
                        case "ban":

                            if(await client.db.fetch(`${interaction.guild.id}.config.ban`) === true) return interaction.reply({content: "<:3595failed:926715200172867624> The configuration has already been set!", ephemeral: true})
                            else {
                                client.db.set(`${interaction.guild.id}.config.ban`, true)
                                interaction.reply({content: "<:9294passed:926715199950561341> Configuration updated!", ephemeral: true})
                            }

                            break
                        case "kick":
                            if(await client.db.fetch(`${interaction.guild.id}.config.kick`) === true) return interaction.reply({content: "<:3595failed:926715200172867624> The configuration has already been set!", ephemeral: true})
                            else {
                                client.db.set(`${interaction.guild.id}.config.kick`, true)
                                interaction.reply({content: "<:9294passed:926715199950561341> Configuration updated!", ephemeral: true})
                            }
                            break;
                        case "timeout":
                            if(await client.db.fetch(`${interaction.guild.id}.config.timeout`) === true) return interaction.reply({content: "<:3595failed:926715200172867624> The configuration has already been set!", ephemeral: true})
                            else {
                                client.db.set(`${interaction.guild.id}.config.timeout`, true)
                                interaction.reply({content: "<:9294passed:926715199950561341> Configuration updated!", ephemeral: true})
                            }
                            break;
                        case "reset":
                            client.db.delete(`${interaction.guild.id}.config.ban`)
                            client.db.delete(`${interaction.guild.id}.config.kick`)
                            client.db.delete(`${interaction.guild.id}.config.timeout`)
                            interaction.reply({content: "<:9294passed:926715199950561341> Configurations have been reset!", ephemeral: true})
                            break;
                    }
                    break

                case "log":
                    const channel = await client.channels.cache.get(interaction.options._hoistedOptions[0].value)
                    if(channel.type !== "GUILD_TEXT") return interaction.reply({content: "<:3595failed:926715200172867624> The channel must be a text channel!", ephemeral: true})
                    const webhooks = await channel.fetchWebhooks();
                    const web = webhooks.find(wh => wh.owner.id === client.user.id);

                    if(web) {
                        return interaction.reply({content: "Looks like logging is already enabled!", ephemeral: true})
                    } else {
                        if(await client.db.fetch(`${interaction.guild.id}.config.log.id`) && await client.db.fetch(`${interaction.guild.id}.config.log.token`)) {
                            return interaction.reply({content: "Looks like logging is already enabled on a different channel! If you wish to change channels, please reset the configuration and run this command again.", ephemeral: true})
                        }
                        const webhook = await channel.createWebhook('Phish Logger', {
                            avatar: client.user.avatarURL()
                        })
                        client.db.set(`${interaction.guild.id}.config.log.channelId`, channel.id)
                        client.db.set(`${interaction.guild.id}.config.log.id`, webhook.id)
                        client.db.set(`${interaction.guild.id}.config.log.token`, webhook.token)

                        interaction.reply({content: `<:9294passed:926715199950561341> ${channel.name} has been set as the log channel.`, ephemeral: true})
                    }

                    break;

                case "reset":

                    switch(value[0].value) {
                        case "delete":
                            client.db.delete(`${interaction.guild.id}.config.delete`)
                            interaction.reply({content: "<:9294passed:926715199950561341> The configuration has been reset!", ephemeral: true})
                            break
                        case "log":
                            const channelFetch = await client.channels.cache.get(await client.db.fetch(`${interaction.guild.id}.config.log.channelId`)).fetchWebhooks();
                            const filter = channelFetch.filter(webhook => webhook.owner.id === client.user.id && webhook.name === 'Phish Logger')
                            if (filter.size === 0) return
                            for (let [id, webhook] of filter) await webhook.delete();
                            client.db.delete(`${interaction.guild.id}.config.log.channelId`)
                            client.db.delete(`${interaction.guild.id}.config.log.id`)
                            client.db.delete(`${interaction.guild.id}.config.log.token`)
                            client.db.delete(`${interaction.guild.id}.config.log.channelId`)

                            interaction.reply({content: "<:9294passed:926715199950561341> The configuration has been reset!", ephemeral: true})
                            break
                        case "action":
                            client.db.delete(`${interaction.guild.id}.config.ban`)
                            client.db.delete(`${interaction.guild.id}.config.kick`)
                            client.db.delete(`${interaction.guild.id}.config.timeout`)
                            interaction.reply({content: "<:9294passed:926715199950561341> The configuration has been reset!", ephemeral: true})
                            break
                        case "all":
                            const loggerWebhook = await client.channels.cache.get(await client.db.fetch(`${interaction.guild.id}.config.log.channelId`)).fetchWebhooks();
                            const deleteFilter = loggerWebhook.filter(webhook => webhook.owner.id === client.user.id && webhook.name === 'Phish Logger')
                            if (deleteFilter.size === 0) return
                            for (let [id, webhook] of deleteFilter) await webhook.delete();
                            client.db.delete(`${interaction.guild.id}.config.delete`)
                            client.db.delete(`${interaction.guild.id}.config.log.channelId`)
                            client.db.delete(`${interaction.guild.id}.config.log.id`)
                            client.db.delete(`${interaction.guild.id}.config.log.token`)
                            client.db.delete(`${interaction.guild.id}.config.ban`)
                            client.db.delete(`${interaction.guild.id}.config.kick`)
                            client.db.delete(`${interaction.guild.id}.config.timeout`)
                            interaction.reply({content: "<:9294passed:926715199950561341> All configurations have been reset!", ephemeral: true})
                            break
                    }

                    break
            }
        }

    }

    }