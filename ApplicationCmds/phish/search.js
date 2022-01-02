const {MessageEmbed} = require("discord.js");
const moment = require('moment')
module.exports = {
    name: "search",
    description: "Check if a link is flagged as a phishing site.",
    options: [
        {
            name: "domain",
            description: "The domain to search for.",
            type: 3,
            required: true
        }
    ],
    category: "phish",
    run: async(interaction, client) => {
        try {


        const regex = new RegExp(/(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]?/gi);
       const domain = interaction.options._hoistedOptions[0].value.match(regex)[0]
        const inf = await client.phish.linkInfo(domain)
        if(!inf[domain] || inf[domain].classification === 'unknown') return interaction.reply({content: `Could not find any information on the domain \`${domain}\``, ephemeral: true})
        if(inf[domain].classification === 'safe') return interaction.reply({content: `The link \`${domain}\` is not flagged as a phishing site.`})
        let embed = new MessageEmbed()

        let status = inf[`${domain}`].status
        if(status === 'ONLINE') {
            status = "🟢 Online"
        } else {
            status = "🔴 Offline"
        }

        let verified = inf[`${domain}`].verifiedPhish
        verified = !!verified
        if(verified === true) {
            verified = "<:9294passed:926715199950561341> Verified"
        } else {
            verified = "<:3595failed:926715200172867624> Not Verified"
        }

        let classification = inf[`${domain}`].classification
        if(classification === 'suspicious') {
            embed.setColor("YELLOW")
            classification = "❗ Suspicious"
        } else if(classification === 'malicious') {
            embed.setColor('RED')
            classification = "<:6371win11warningicon:926716233724870696> Malicious"
        }

        let firstSeen = inf[`${domain}`].firstSeen
        if(!firstSeen) firstSeen = Date.now()

        let lastSeen = inf[`${domain}`].lastSeen
        if(!lastSeen) lastSeen = Date.now()

        embed
            .setDescription(domain)
            .addField("__Status__", status, true)
            .addField("__Verified__", verified, true)
            .addField("__Classification__", classification, true)
            .addField("__Added__", `<t:${moment(inf[`${domain}`].created).format("X")}:F>`, true)
            .addField("__First Seen__", `<t:${moment(firstSeen).format("X")}:F>`, true)
            .addField("__Last Seen__", `<t:${moment(lastSeen).format("X")}:F>`, true)
            .addField('__Domain IP__', `${inf[`${domain}`].details.ip_address ? inf[`${domain}`].details.ip_address : 'IP address not found.'}`, true)
            .addField('__Asn Name__', inf[`${domain}`].details.asn.asn_name ? inf[`${domain}`].details.asn.asn_name : 'No asn name found.', true)
            .setImage(inf[`${domain}`].details.websiteScreenshot)

        interaction.reply({embeds: [embed]})

        } catch(e) {
            return interaction.reply({content: "Looks like something went wrong. Make sure you're inputting a domain or link.", ephemeral: true})
        }
    }
}