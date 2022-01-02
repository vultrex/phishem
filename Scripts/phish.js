const fetch = require('node-fetch');
const Discord = require("discord.js");
const {MessageActionRow, MessageButton, MessageEmbed} = require("discord.js");

/**
 *
 * @param link The link that will get checked.
 * @returns {Promise<any>}
 */
async function checkLink(link) {
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
async function linkInfo(domain) {
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
async function checkYoutube(link) {
    return !![process.env.youtubeKeywords].find(async x => {
        const regex = new RegExp(`\\b${x}\\b`, 'i');
        return regex.test(await require('node-fetch')(link).then(res => res.text()))
    })
}


async function logger(webhookID, webhookToken, user, link, message, time) {
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
        embeds: [
            new Discord.MessageEmbed()
                .setColor('#ff0000')
                .setThumbnail(user.avatarURL({dynamic: true}))
                .setTitle(`<:3595failed:926715200172867624> Malicious link detected!`)
                .setDescription(`<@${user.id}> ${user.tag} | ${user.id}\nsent a malicious link <t:${time}:R>.\n\nDeleted Message: ${message}`)
        ],
        components: [
            urlscan
        ]
    })
}

async function youtubeLogger(webhookID, webhookToken, user, link, message, time) {
    const webhook = new Discord.WebhookClient({
        id: webhookID,
        token: webhookToken
    });

    await webhook.send({
        embeds: [
            new Discord.MessageEmbed()
                .setColor('#ff0000')
                .setThumbnail(user.avatarURL({dynamic: true}))
                .setTitle(`<:3595failed:926715200172867624> Potential malicious Youtube video found`)
                .setDescription(`<@${user.id}> ${user.tag} | ${user.id}\nsent a malicious Youtube video <t:${time}:R>.\n\nDeleted Message: ${message}`)
        ]
    })
}

module.exports = {
    checkLink,
    linkInfo,
    checkYoutube,
    logger,
    youtubeLogger
}