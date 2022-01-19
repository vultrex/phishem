const Schema = require("../../Database/Schema/Guild");
module.exports = {
    name: "reset",
    description: "Resets the configurations for the server.",
    options: [
        {
            name: "infractions",
            description: "Resets the user's infractions.",
            type: 6,
        },
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
                    name: "Staff-bypass",
                    value: "sBypass"
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
                    name: "Action",
                    value: "action"
                },
                {
                    name: "Domains",
                    value: "domains"
                },
                {
                    name: "All",
                    value: "all"
                },
                ]

        },

    ],
    permissions: "MANAGE_GUILD",
    category: "phish",
    run: async(interaction,  client) => {
        Schema.findOne({id: interaction.guild.id}, async (err, data) => {
            switch(interaction.options._hoistedOptions[0].name) {
                case "infractions":
                    console.log(interaction.options._hoistedOptions[0].value)
                    break
            }

            switch (interaction.options._hoistedOptions[0].value) {
                case "delete":
                    data.config.delete = false
                    data.save()
                    interaction.reply({
                        content: "<:9294passed:926715199950561341> The configuration has been reset!",
                        ephemeral: true
                    })
                    break
                case "sBypass":
                    data.config.ignore_staff = true
                    data.save()
                    interaction.reply({
                        content: "<:9294passed:926715199950561341> The configuration has been updated!",
                        ephemeral: true
                    })
                    break
                case "log":
                    if (await client.channels.cache.get(data.log.webhookChannelID)) {
                        const loggerWebhook = await client.channels.cache.get(data.log.webhookChannelID).fetchWebhooks()
                        const deleteFilter = loggerWebhook.filter(webhook => webhook.owner.id === client.user.id && webhook.name === 'Phish Logger')
                        if (deleteFilter) for (let [id, webhook] of deleteFilter) await webhook.delete();

                    }

                    data.log.webhookID = null
                    data.log.webhookID = null
                    data.log.webhookChannelID = null
                    await data.save()

                    interaction.reply({
                        content: "<:9294passed:926715199950561341> The configuration has been reset!",
                        ephemeral: true
                    })
                    break
                case "action":
                    data.config.action_ban = false
                    data.config.action_kick = false
                    data.config.action_timeout = false
                    await data.save()
                    interaction.reply({
                        content: "<:9294passed:926715199950561341> The configuration has been reset!",
                        ephemeral: true
                    })
                    break
                case "youtube":
                    data.config.youtube_filter = false
                    data.save()
                    interaction.reply({
                        content: "<:9294passed:926715199950561341> The configuration has been reset!",
                        ephemeral: true
                    })
                    break
                case "domains":
                    data.config.bypass = []
                    data.save()
                    interaction.reply({
                        content: "<:9294passed:926715199950561341> The configuration has been reset!",
                        ephemeral: true
                    })
                    break
                case "all":

                    if (await client.channels.cache.get(data.log.webhookChannelID)) {
                        const loggerWebhook = await client.channels.cache.get(data.log.webhookChannelID).fetchWebhooks()
                        const deleteFilter = loggerWebhook.filter(webhook => webhook.owner.id === client.user.id && webhook.name === 'Phish Logger')
                        if (deleteFilter) for (let [id, webhook] of deleteFilter) await webhook.delete();

                    }
                    data.log.webhookID = null
                    data.log.webhookToken = null
                    data.log.webhookChannelID = null
                    data.config.ignore_staff = true
                    data.config.action_ban = false
                    data.config.action_kick = false
                    data.config.action_timeout = false
                    data.config.youtube_filter = false
                    data.config.delete = false
                    data.save()
                    interaction.reply({
                        content: "<:9294passed:926715199950561341> All configurations have been reset!",
                        ephemeral: true
                    })


                    break
            }
        })


    }
}
