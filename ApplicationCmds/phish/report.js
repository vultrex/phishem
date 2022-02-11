const {WebhookClient, MessageEmbed} = require("discord.js");
module.exports = {
    name: "report",
    description: "Report a malicious domain/link [STILL IN DEVELOPMENT]",
    options: [],
    category: "phish",
    timeout: 600000,
    run: async (int, client) => {

        int.reply({
            content: "Click the button below to start your report",
            components: [
                {
                    type: 1, components: [
                        { type: 2, style: 3, custom_id: 'modal_open', label: 'Start the report' }
                    ]
                }
            ],
        })
        setTimeout(() => int.deleteReply(), 20000)
        const antiPing = (text) => text.replace(/`/g, `\`${String.fromCharCode(8203)}`).replace(/@/g, `@${String.fromCharCode(8203)}`);
        const truncate = (length, text) => antiPing(text.slice(0, length) + (text.length > length ? '...' : ''));

        client.ws.on('INTERACTION_CREATE', async (interaction) => {
            try {


const id = Math.floor(Math.random() * 100)
                const cID = [];
                if (interaction.data.custom_id === 'modal_open') return client.api.interactions(interaction.id)[interaction.token].callback.post({
                    data: {
                        type: 9,
                        data: {
                            title: 'Report a domain',
                            custom_id: id,
                            components: [
                                {
                                    type: 1,
                                    components: [
                                        {
                                            type: 4,
                                            style: 1,
                                            custom_id: 'report field',
                                            label: 'What\'s the domain you want to report?'
                                        }
                                    ]
                                },
                            ]
                        }
                    }
                });
                cID.push(interaction.data.custom_id)
                if (interaction.data.custom_id === cID[0]) {
                    const reg = new RegExp(/(?:[A-z0-9](?:[A-z0-9-]{0,61}[A-z0-9])?\.)+[A-z0-9][A-z0-9-]{0,61}[A-z0-9]/gi)

                    if(!reg.test(truncate(1010, interaction.data.components[0].components[0].value))) {
                        return client.api.interactions(interaction.id)[interaction.token].callback.post({
                            data: {
                                type: 4,
                                data: {
                                    flags: 1 << 6,
                                    content: "Please enter a valid domain",
                                    ephemeral: true
                                }
                            }
                        });

                    }

                    if(!await client.phish.bit(truncate(1010, interaction.data.components[0].components[0].value))) {
                        return client.api.interactions(interaction.id)[interaction.token].callback.post({
                            data: {
                                type: 4,
                                data: {
                                    flags: 1 << 6,
                                    content: "This domain is already flagged",
                                    ephemeral: true
                                }
                            }
                        });
                    }
                    await int.deleteReply()
                    const webhook = new WebhookClient({
                        id: "941217050871877704",
                        token: "Wg2_6F6jjnESXM4HcPwqtCAbZ7dbnxkDt4gI8-RxXGESp0gjpdPVkh9ZWOkhRW8HCM-Z"
                    });

                    await webhook.send({
                        name: "phish reports",
                        content: "<@!750510159289254008>",
                        embeds: [new MessageEmbed().setColor("RED").setThumbnail(int.member.user.avatarURL()).setDescription(`The domain \`${truncate(1010, interaction.data.components[0].components[0].value)}\` has been reported by ${int.member.user.tag} (${int.member.user.id})`).setFooter({
                            text: int.guild.name + " | " + int.guild.id,
                            iconURL: int.guild.iconURL()
                        })]
                    })
                    return client.api.interactions(interaction.id)[interaction.token].callback.post({
                        data: {
                            type: 4,
                            data: {
                                flags: 1 << 6,
                                content: `Your report \`${truncate(1010, interaction.data.components[0].components[0].value)}\` has been sent to be reviewed.`
                            }
                        }
                    });
                }
            } catch(e) {
                await int.deleteReply()
                return client.api.interactions(interaction.id)[interaction.token].callback.post({
                    data: {
                        type: 4,
                        data: {
                            flags: 1 << 6,
                            content: "Looks like something went wrong, try and execute this command again."
                        }
                    }
                })
            }
        })
    }
}