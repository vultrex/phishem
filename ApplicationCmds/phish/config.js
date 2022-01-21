const { MessageEmbed, Permissions } = require('discord.js'),
    Schema = require("../../Database/Schema/Guild")

module.exports = {
    name: "configure",
    description: "Set the configuration for your server",
    options: [
        {
            name: "get",
            description: "Get the current configuration",
            type: 1,
        },
        /*
        {
            name: "block",
            description: "Add additional domains to the filters to block",
            type: 2,
            options: [
                {
                    name: "domain",
                    description: "Add or remove domains that will bypass the filters",
                    type: 1,
                    options: [
                        {
                            name: "add",
                            description: "Add a domain to block",
                            type: 3,
                        },
                        {
                            name: "remove",
                            description: "Remove the blocked domains.",
                            type: 3,
                        },
                    ]

                },

            ]
        },
         */
        {
            name: "bypass",
            description: "Create or remove links that will bypass the filters",
            type: 2,
            options: [
                {
                    name: "domain",
                    description: "Add or remove domains that will bypass the filters",
                    type: 1,
                    options: [
                        {
                            name: "add",
                            description: "Add a domain to bypass the filters",
                            type: 3,
                        },
                        {
                            name: "remove",
                            description: "Remove a domain from the bypass",
                            type: 3,
                        },
                    ]

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
                  name: "staff-bypass",
                    description: "If staff members should be able to bypass the filters.",
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
        ],
    permissions: "MANAGE_GUILD",
    category: "phish",
    run: async(interaction,  client) => {

        Schema.findOne({id: interaction.guild.id}, async (err, data) => {

        switch(interaction.options._subcommand) {
            case "get":

                    if(data) {
                        let configEmbed = new MessageEmbed()
                            .setTitle(`The current configuration for \`${interaction.guild.name}\``)
                            .setColor(0x00AE86)
                            .setDescription(`\`\`\`diff\n++++ Server Configurations ++++\n${data.config.delete ? "+" : "-"} Delete Links: ${data.config.delete ? "On" : "Off"}\n${data.config.youtube_filter ? "+" : "-"} Youtube Filter: ${data.config.youtube_filter ? "On" : "Off"}\n${data.log.webhookID && data.log.webhookToken ? "+" : "-"} Logging: ${data.log.webhookID && data.log.webhookToken ? "On" : "Off"}\n  Actions:\n${data.config.action_ban ? "+" : "-"} Ban: ${data.config.action_ban ? "On" : "off"}\n${data.config.action_kick ? "+" : "-"} Kick: ${data.config.action_kick ? "On" : "Off"}\n${data.config.action_timeout ? "+" : "-"} Timeout: ${data.config.action_timeout ? "On" : "Off"}\`\`\`\n\`\`\`diff\n++++ Domains That Bypass The Filters ++++\n${data.config.bypass.join("\n") ? data.config.bypass.join("\n") : "None have been added."}\`\`\``)
                        return interaction.reply({embeds: [configEmbed]});
                    }

                break

            case "domain":
                if(!data.config.bypass) {
                    const newData = new Schema({
                        id: interaction.guild.id,
                        name: interaction.guild.name,
                        config: {
                            bypass: []
                        }
                    })
                    return await newData.save()
                }
                const link = new RegExp(/(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]?/gi)
                if(!interaction.options._hoistedOptions[0]) return interaction.reply({content: "<:3595failed:926715200172867624> You must specify a option!", ephemeral: true})
                if(interaction.options._hoistedOptions.length > 1) return interaction.reply({content: "<:3595failed:926715200172867624> You can only specify one option!", ephemeral: true})
                const string = interaction.options._hoistedOptions[0].value;
                switch(interaction.options._hoistedOptions[0].name) {

                    case "add":
                        if(!interaction.options._hoistedOptions[0]) return interaction.reply({content: "<:3595failed:926715200172867624> You must specify a option!", ephemeral: true})
                        if(interaction.options._hoistedOptions.length > 1) return interaction.reply({content: "<:3595failed:926715200172867624> You can only specify one option!", ephemeral: true})

                        if(link.test(string)) {
                            const httpReg = new RegExp(/(https?:\/\/[^\s]+)/g)
                            if(data.config.bypass.includes(string)) return interaction.reply({content: "<:3595failed:926715200172867624> This domain is already in the bypass list!", ephemeral: true})
                            data.config.bypass.push(string)
                            await data.save()
                            return interaction.reply({content: `<:9294passed:926715199950561341> The domain \`${string}\` has been added to the list of domains to be filtered.`, ephemeral: true})
                        } else {
                            interaction.reply({content: "<:3595failed:926715200172867624> The domain you provided is not a valid.", ephemeral: true})
                        }

                        break
                    case "remove":
                        if(!interaction.options._hoistedOptions[0]) return interaction.reply({content: "<:3595failed:926715200172867624> You must specify a option!", ephemeral: true})
                        if(interaction.options._hoistedOptions.length > 1) return interaction.reply({content: "<:3595failed:926715200172867624> You can only specify one option!", ephemeral: true})
                    function removeItemOnce(arr, value) {
                        const index = arr.indexOf(value);
                        if (index > -1) {
                            arr.splice(index, 1);
                        }
                        return arr;
                    }
                        if(link.test(string)){
                            if(!data.config.bypass.includes(string)) return interaction.reply({content: "<:3595failed:926715200172867624> This domain is not in the bypass list, so there's nothing to remove!", ephemeral: true})
                            removeItemOnce(data.config.bypass, string)
                            data.save()
                            return interaction.reply({content: `<:9294passed:926715199950561341> The domain \`${string}\` has been removed from the list of domains to be filtered.`, ephemeral: true})
                        }
                        break

                }

                break
            case "set":
                if(!interaction.options._hoistedOptions[0]) return interaction.reply({content: "<:3595failed:926715200172867624> You must specify a option!", ephemeral: true})
                if(interaction.options._hoistedOptions.length > 1) return interaction.reply({content: "<:3595failed:926715200172867624> You can only specify one option!", ephemeral: true})

                const value = interaction.options._hoistedOptions
                if(value[0]) {

                    Schema.findOne({id: interaction.guild.id}, async (err, data) => {

                        switch(interaction.options._hoistedOptions[0].name) {
                            case "delete":
                                if (!interaction.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return interaction.reply({
                                    content: "<:3595failed:926715200172867624> I don't have the `Manage Messages` permission!",
                                    ephemeral: true
                                })
                                if (!interaction.options._hoistedOptions[0].value) {
                                    if(!data.config.delete) return interaction.reply({content: "<:3595failed:926715200172867624> Message deletion is already disabled.", ephemeral: true})
                                    if (data) {
                                        if (data.config.delete) {
                                            data.config.delete = false
                                            await data.save()
                                            return interaction.reply({
                                                content: "<:9294passed:926715199950561341> Message deletion has been disabled.",
                                                ephemeral: true
                                            })

                                        }
                                    }
                                } else {
                                    if(data.config.delete) return interaction.reply({content: "<:3595failed:926715200172867624> Message deletion is already enabled.", ephemeral: true})
                                    data.config.delete = true
                                    await data.save()
                                    return interaction.reply({
                                        content: "<:9294passed:926715199950561341> Message deletion has been enabled.",
                                        ephemeral: true
                                    })
                                }


                                break
                            case "staff-bypass":
                                if (!interaction.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return interaction.reply({
                                    content: "<:3595failed:926715200172867624> I don't have the `Manage Messages` permission!",
                                    ephemeral: true
                                })
                                if (!interaction.options._hoistedOptions[0].value) {
                                    if(!data.config.ignore_staff) return interaction.reply({content: "<:3595failed:926715200172867624> This setting is already disabled.", ephemeral: true})
                                    if (data) {
                                        if (data.config.ignore_staff) {
                                            data.config.ignore_staff = false
                                            await data.save()
                                            return interaction.reply({
                                                content: "<:9294passed:926715199950561341> The staff bypass filters have been turned off.",
                                                ephemeral: true
                                            })

                                        }
                                    }


                                } else {

                                    if (data.config.ignore_staff) return interaction.reply({
                                        content: "<:3595failed:926715200172867624> This option is already enabled.",
                                        ephemeral: true
                                    })
                                    if (!data.config.ignore_staff) {
                                        data.config.ignore_staff = true
                                        await data.save()
                                        return interaction.reply({
                                            content: "<:9294passed:926715199950561341> Successfully configured, I will now ignore staff members who have `MANAGE_GUILD`, `MANAGE_MESSAGES`, and `MODERATE_MEMBERS`",
                                            ephemeral: true
                                        })
                                    }


                                }
                                break
                            case "youtube-filter":

                                if (!interaction.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return interaction.reply({
                                    content: "<:3595failed:926715200172867624> I don't have the `Manage Messages` permission!",
                                    ephemeral: true
                                })

                                if (!interaction.options._hoistedOptions[0].value) {
                                    if(!data.config.youtube_filter) return interaction.reply({content: "<:3595failed:926715200172867624> The youtube filter is already disabled!", ephemeral: true})
                                    if (data) {
                                        if (data.config.youtube_filter) {
                                            data.config.youtube_filter = false
                                            await data.save()
                                            return interaction.reply({
                                                content: "<:9294passed:926715199950561341> The youtube filters have been turned off.",
                                                ephemeral: true
                                            })

                                        }
                                    }


                                } else {


                                    if (data) {
                                        if(data.config.youtube_filter) return interaction.reply({content: "<:3595failed:926715200172867624> The youtube filter is already enabled!", ephemeral: true})

                                        data.config.youtube_filter = true
                                        await data.save()
                                        return interaction.reply({
                                            content: "<:9294passed:926715199950561341> Successfully configured, I will now filter youtube videos that get sent.",
                                            ephemeral: true
                                        })
                                    }


                                }
                                break
                            case "action":


                                switch (value[0].value) {
                                    case "ban":


                                        if (data) {
                                            if (data.config.action_kick) return interaction.reply({
                                                content: "<:3595failed:926715200172867624> You can't enable both kick and ban.",
                                                ephemeral: true
                                            })
                                            if (data.config.action_ban) return interaction.reply({
                                                content: "<:3595failed:926715200172867624> The configuration has already been set!",
                                                ephemeral: true
                                            })
                                            else {
                                                if (!interaction.guild.me.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return interaction.reply({
                                                    content: "<:3595failed:926715200172867624> I don't have the `Ban Members` permission!",
                                                    ephemeral: true
                                                })
                                                data.config.action_ban = true
                                                await data.save()
                                                return interaction.reply({
                                                    content: "<:9294passed:926715199950561341> Configuration updated!",
                                                    ephemeral: true
                                                })
                                            }
                                        }


                                        break
                                    case "kick":

                                        if (data) {
                                            if (data.config.action_ban) return interaction.reply({
                                                content: "<:3595failed:926715200172867624> You can't enable both kick and ban.",
                                                ephemeral: true
                                            })
                                            if (data.config.action_kick) return interaction.reply({
                                                content: "<:3595failed:926715200172867624> The configuration has already been set!",
                                                ephemeral: true
                                            })
                                            else {
                                                if (!interaction.guild.me.permissions.has(Permissions.FLAGS.KICK_MEMBERS)) return interaction.reply({
                                                    content: "<:3595failed:926715200172867624> I don't have the `Kick Members` permission!",
                                                    ephemeral: true
                                                })
                                                data.config.action_kick = true
                                                await data.save()
                                                return interaction.reply({
                                                    content: "<:9294passed:926715199950561341> Configuration updated!",
                                                    ephemeral: true
                                                })
                                            }
                                        }

                                        break;
                                    case "timeout":


                                        if (data) {
                                            if (data.config.action_timeout) return interaction.reply({
                                                content: "<:3595failed:926715200172867624> The configuration has already been set!",
                                                ephemeral: true
                                            })
                                            else {
                                                if (!interaction.guild.me.permissions.has(Permissions.FLAGS.MODERATE_MEMBERS)) return interaction.reply({
                                                    content: "<:3595failed:926715200172867624> I don't have the `Moderate Members` permission!",
                                                    ephemeral: true
                                                })
                                                data.config.action_timeout = true
                                                await data.save()
                                                return interaction.reply({
                                                    content: "<:9294passed:926715199950561341> Configuration updated!",
                                                    ephemeral: true
                                                })
                                            }
                                        }

                                        break;
                                    case "reset":
                                        data.config.action_ban = false
                                        data.config.action_kick = false
                                        data.config.action_timeout = false
                                        await data.save()
                                        interaction.reply({
                                            content: "<:9294passed:926715199950561341> Configurations have been reset!",
                                            ephemeral: true
                                        })
                                        break;
                                }
                                break

                            case "log":
                                const channel = await client.channels.cache.get(interaction.options._hoistedOptions[0].value)
                                if (channel.type !== "GUILD_TEXT") return interaction.reply({
                                    content: "<:3595failed:926715200172867624> The channel must be a text channel!",
                                    ephemeral: true
                                })
                                const webhooks = await channel.fetchWebhooks();
                                const web = webhooks.find(wh => wh.owner.id === client.user.id);

                                if (data.log.webhookID && data.log.webhookToken) {
                                    return interaction.reply({
                                        content: "Looks like logging is already enabled on a different channel! If you wish to change channels, please reset the configuration and run this command again.",
                                        ephemeral: true
                                    })
                                } else {
                                    const webhook = await channel.createWebhook('Phish Logger', {
                                        avatar: client.user.avatarURL({format: 'png'}),
                                    })
                                    data.log.webhookID = webhook.id
                                    data.log.webhookToken = webhook.token
                                    data.log.webhookChannelID = channel.id
                                    data.save()
                                    interaction.reply({
                                        content: `<:9294passed:926715199950561341> \`${channel.name}\` has been set as the log channel.`,
                                        ephemeral: true
                                    })
                                }


                                break;


                        }
                    })
                }
                break
        }
        })



    }

    }