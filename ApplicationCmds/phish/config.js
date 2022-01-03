const { MessageEmbed } = require('discord.js');

module.exports = {
    name: "configure",
    description: "Set the configuration for your server",
    options: [
        {
            name: "get",
            description: "Get the current configuration",
            type: 1,
        },
        {
            name: "bypass",
            description: "Create or remove links that will bypass the filters",
            type: 1,
            options: [
                {
                    name: "create",
                    description: "Create a bypass link",
                    type: 3,
                },
                {
                    name: "remove",
                    description: "Remove a bypass link",
                    type: 3,
                },
            ]
        },
        {
            name: "set",
            description: "Set configuration for your server",
            type: 1,
            options: [
                {
                    name: "delete",
                    description: "If the detected phishing links should be deleted.",
                    type: 5,
                },
                {
                    name: "youtube-filter",
                    description: "Scan and filter \"free nitro generator\" youtube videos.",
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
                    name: "configurations",
                    description: "Reset the server configurations back to it's original state.",
                    type: 3,
                    choices: [
                        {
                            name: "Delete",
                            value: "delete"
                        },
                        {
                            name: "Youtube-filter",
                            value: "youtube"
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
    permissions: "MANAGE_GUILD",
    category: "phish",
    run: async(interaction,  client) => {
        switch(interaction.options._subcommand) {
            case "get":
                let configEmbed = new MessageEmbed()
                    .setTitle(`The current configuration for \`${interaction.guild.name}\``)
                    .setColor(0x00AE86)
                    .setDescription(`\`\`\`diff\n++++ Server Configurations ++++\n${await client.db.fetch(`${interaction.guild.id}.config.delete`) ? "+" : "-"} Delete Links: ${await client.db.fetch(`${interaction.guild.id}.config.delete`) ? "On" : "Off"}\n${await client.db.fetch(`${interaction.guild.id}.config.youtube`) ? "+" : "-"} Youtube Filter: ${await client.db.fetch(`${interaction.guild.id}.config.youtube`) ? "On" : "Off"}\n${await client.db.fetch(`${interaction.guild.id}.config.log.id`) ? "+" : "-"} Logging: ${await client.db.fetch(`${interaction.guild.id}.config.log.id`) ? "On" : "Off"}\n  Actions:\n${await client.db.fetch(`${interaction.guild.id}.config.ban`) ? "+" : "-"} Ban: ${await client.db.fetch(`${interaction.guild.id}.config.ban`) ? "On" : "off"}\n${await client.db.fetch(`${interaction.guild.id}.config.kick`) ? "+" : "-"} Kick: ${await client.db.fetch(`${interaction.guild.id}.config.kick`) ? "On" : "Off"}\n${await client.db.fetch(`${interaction.guild.id}.config.timeout`) ? "+" : "-"} Timeout: ${await client.db.fetch(`${interaction.guild.id}.config.guild`) ? "On" : "Off"}\`\`\``)
                interaction.reply({embeds: [configEmbed]});
                break

            case "bypass":
                if(!interaction.options._hoistedOptions[0]) return interaction.reply({content: "<:3595failed:926715200172867624> You must specify a option!", ephemeral: true})
                if(interaction.options._hoistedOptions.length > 1) return interaction.reply({content: "<:3595failed:926715200172867624> You can only specify one option!", ephemeral: true})
                const string = interaction.options._hoistedOptions[0].value;
                switch(interaction.options._hoistedOptions[0].name) {

                    case "create":
                        if(!interaction.options._hoistedOptions[0]) return interaction.reply({content: "<:3595failed:926715200172867624> You must specify a option!", ephemeral: true})
                        if(interaction.options._hoistedOptions.length > 1) return interaction.reply({content: "<:3595failed:926715200172867624> You can only specify one option!", ephemeral: true})
                        interaction.reply({content: 'This command is still being worked on!', ephemeral: true})
                        break
                    case "remove":
                        interaction.reply({content: 'This command is still being worked on!', ephemeral: true})
                        break

                }

                break
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
                case "youtube-filter":
                    if(await client.db.fetch(`${interaction.guild.id}.config.youtube`)) return interaction.reply({content: "<:3595failed:926715200172867624> Youtube links are already being filtered.", ephemeral: true})
                    client.db.set(`${interaction.guild.id}.config.youtube`, interaction.options._hoistedOptions[0].value)
                    interaction.reply({content: "<:9294passed:926715199950561341> Successfully configured, I will now filter youtube videos that get sent.", ephemeral: true})
                    break
                case "action":

                    switch(value[0].value) {
                        case "ban":
                            if(await client.db.fetch(`${interaction.guild.id}.config.kick`) == true) return interaction.reply({content: "<:3595failed:926715200172867624> You can't enable both kick and ban.", ephemeral: true})
                            if(await client.db.fetch(`${interaction.guild.id}.config.ban`) === true) return interaction.reply({content: "<:3595failed:926715200172867624> The configuration has already been set!", ephemeral: true})
                            else {
                                client.db.set(`${interaction.guild.id}.config.ban`, true)
                                interaction.reply({content: "<:9294passed:926715199950561341> Configuration updated!", ephemeral: true})
                            }

                            break
                        case "kick":
                            if(await client.db.fetch(`${interaction.guild.id}.config.ban`) == true) return interaction.reply({content: "<:3595failed:926715200172867624> You can't enable both kick and ban.", ephemeral: true})
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
                            avatar: client.user.avatarURL({format: 'png'}),
                        })
                        client.db.set(`${interaction.guild.id}.config.log.channelId`, channel.id)
                        client.db.set(`${interaction.guild.id}.config.log.id`, webhook.id)
                        client.db.set(`${interaction.guild.id}.config.log.token`, webhook.token)

                        interaction.reply({content: `<:9294passed:926715199950561341> \`${channel.name}\` has been set as the log channel.`, ephemeral: true})
                    }

                    break;

                case "configurations":

                    switch(value[0].value) {
                        case "delete":
                            client.db.delete(`${interaction.guild.id}.config.delete`)
                            interaction.reply({content: "<:9294passed:926715199950561341> The configuration has been reset!", ephemeral: true})
                            break
                        case "log":
                            if(await client.channels.cache.get(await client.db.fetch(`${interaction.guild.id}.config.log.channelId`))) {
                                const loggerWebhook = await client.channels.cache.get(await client.db.fetch(`${interaction.guild.id}.config.log.channelId`)).fetchWebhooks()
                                const deleteFilter = loggerWebhook.filter(webhook => webhook.owner.id === client.user.id && webhook.name === 'Phish Logger')
                                if(deleteFilter) for (let [id, webhook] of deleteFilter) await webhook.delete();

                            }
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
                        case "youtube":
                            client.db.delete(`${interaction.guild.id}.config.youtube`)
                            interaction.reply({content: "<:9294passed:926715199950561341> The configuration has been reset!", ephemeral: true})
                            break
                        case "all":

                            if(await client.channels.cache.get(await client.db.fetch(`${interaction.guild.id}.config.log.channelId`))) {
                                const loggerWebhook = await client.channels.cache.get(await client.db.fetch(`${interaction.guild.id}.config.log.channelId`)).fetchWebhooks()
                                const deleteFilter = loggerWebhook.filter(webhook => webhook.owner.id === client.user.id && webhook.name === 'Phish Logger')
                                if(deleteFilter) for (let [id, webhook] of deleteFilter) await webhook.delete();

                            }
                                client.db.delete(`${interaction.guild.id}.config.delete`)
                                client.db.delete(`${interaction.guild.id}.config.log.channelId`)
                                client.db.delete(`${interaction.guild.id}.config.log.id`)
                                client.db.delete(`${interaction.guild.id}.config.log.token`)
                                client.db.delete(`${interaction.guild.id}.config.youtube`)
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