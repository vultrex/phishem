const fetch = require('node-fetch');
const Discord = require("discord.js");
const {MessageActionRow, MessageButton, MessageEmbed} = require("discord.js");
const fs = require("fs");

/**
 *
 * @param link The link that will get checked.
 * @returns {Promise<any>}
 */
async function bitFlow(link) {
    return await fetch("https://anti-fish.bitflow.dev/check", {
        method: "post",
        body: JSON.stringify({message: link}),
        headers: {
            "Content-Type": "application/json",
            "User-Agent": "Phishem (Nek#2937 / 750510159289254008)",
        },

    }).then(res => res.json())
}

/**
 *
 * @param domain The domain link to check
 * @returns {Promise<any>}
 */
async function phisherman(domain) {

    return await fetch(`https://api.phisherman.gg/v1/domains/info/${domain}`, {
        headers: {
            "Authorization": 'Bearer 02e6fac0-b924-48aa-b583-2d410fbc691a',
            'Content-Type': 'application/json',
            "User-Agent": "Phishem (Nek#2937 / 750510159289254008)",
        },
    }).then(res => res.json())
}

/**
 *
 * @param link A youtube link that'll get scanned
 * @returns {Promise<boolean>}
 */
async function searchYouTube(link) {

    return !!["discord nitro generator","free nitro generator", "nitro","discord nitro codes generator"].find(async x => {
        const regex = new RegExp(`\\b${x}\\b`, 'i')
        return regex.test(await require('node-fetch')(link).then(res => res.text()))
    })
}


async function logger(webhookID, webhookToken, user, link, message, channel, time) {
    try {


   const phishman = await fetch(`https://api.phisherman.gg/v1/domains/info/${link}`, {
       headers: {
           "Authorization": 'Bearer 02e6fac0-b924-48aa-b583-2d410fbc691a',
           'Content-Type': 'application/json',
           "User-Agent": "Phishem (Nek#2937 / 750510159289254008)",
       },
   }).then(res => res.json())

    const urlscan = new MessageActionRow()
        .addComponents(new MessageButton()
            .setURL(`https://urlscan.io/result/${phishman[link].details.urlScanId}`)
            .setLabel('UrlScan')
            .setEmoji('🛠️')
            .setStyle(5),
        )
    const webhook = new Discord.WebhookClient({
        id: webhookID,
        token: webhookToken
    });


    await webhook.send({
        avatarURL: 'https://media.discordapp.net/attachments/854794095066349618/927378869793718342/blue0517_2.png?width=968&height=605',
        embeds: [
            new Discord.MessageEmbed()
                .setColor('#ff0000')
                .setThumbnail(user.avatarURL({dynamic: true}))
                .setTitle(`<:3595failed:926715200172867624> Malicious link detected!`)
                .setDescription(`<@${user.id}> ${user.tag} | ${user.id}\nsent a malicious link <t:${time}:R> in <#${channel}>.\n\nMessage: \`\`\`${message.length > 1700 ?  "The message was too long to display, refer to the text file below." : message}\`\`\`\nLink Sent:\n\`\`\`${link}\`\`\``)
        ],
        components: [
            urlscan
        ]
    })

    if(message.length > 1700) {
        fs.writeFile(`./phishLog.txt`, `[${user.tag} | ${user.id}]\n${message}`, function (err) {
            if (err) {
                console.log(`[ Error ] `.red + err);
            }
        });

        await webhook.send({
            files: ["./phishLog.txt"]
        })
        setTimeout(async () => {
            fs.unlink(`./phishLog.txt`, function (err) {
                if (err) {
                    console.log(`[ Error ] `.red + err);
                }
            });
        }, 1000);
    }
    } catch (e) {
        const webhook = new Discord.WebhookClient({
            id: webhookID,
            token: webhookToken
        });

        await webhook.send({
            avatarURL: 'https://media.discordapp.net/attachments/854794095066349618/927378869793718342/blue0517_2.png?width=968&height=605',
            embeds: [
                new Discord.MessageEmbed()
                    .setColor('#ff0000')
                    .setThumbnail(user.avatarURL({dynamic: true}))
                    .setTitle(`<:3595failed:926715200172867624> Malicious link detected!`)
                    .setDescription(`<@${user.id}> ${user.tag} | ${user.id}\nsent a malicious link <t:${time}:R> in <#${channel}>.\n\nMessage: \`\`\`${message.length > 1700 ? "The message was too long to display, refer to the text file below." : message}\`\`\`\nLink Sent:\n\`\`\`${link}\`\`\``)
            ],
        })

        if(message.length > 1700) {
            fs.writeFile(`./phishLog.txt`, `[${user.tag} | ${user.id}]\n${message}`, function (err) {
                if (err) {
                    console.log(`[ Error ] `.red + err);
                }
            });

            await webhook.send({
                files: ["./phishLog.txt"]
            })
            setTimeout(async () => {
                fs.unlink(`./phishLog.txt`, function (err) {
                    if (err) {
                        console.log(`[ Error ] `.red + err);
                    }
                });
            }, 1000);
        }
    }
}

async function youtubeLogger(webhookID, webhookToken, user, link, message, channel, time) {
    const webhook = new Discord.WebhookClient({
        id: webhookID,
        token: webhookToken
    });



    await webhook.send({
        avatarURL: 'https://media.discordapp.net/attachments/854794095066349618/927378869793718342/blue0517_2.png?width=968&height=605',
        embeds: [
            new Discord.MessageEmbed()
                .setColor('#ff0000')
                .setThumbnail(user.avatarURL({dynamic: true}))
                .setTitle(`<:3595failed:926715200172867624> Potential Malicious Youtube Video Found`)
                .setDescription(`<@${user.id}> ${user.tag} | ${user.id}\nsent a potential malicious Youtube video <t:${time}:R> in <#${channel}>.\n\nMessage: \n\`\`\`${message.length > 1700 ?  "The message was too long to display, refer to the text file below." : message}\`\`\`\nLink Sent:\n\`\`\`${link}\`\`\``)
        ],
    })

    if(message.length > 1700) {
        fs.writeFile(`./ytphishLog.txt`, `[${user.tag} | ${user.id}]\n${message}`, function (err) {
            if (err) {
                console.log(`[ Error ] `.red + err);
            }
        });

            await webhook.send({
                files: ["./ytphishLog.txt"]
            })
        setTimeout(async () => {
            fs.unlink(`./ytphishLog.txt`, function (err) {
                if (err) {
                    console.log(`[ Error ] `.red + err);
                }
            });
        }, 1000);
    }
}

module.exports = {
    bitFlow,
    phisherman,
    searchYouTube,
    logger,
    youtubeLogger
}