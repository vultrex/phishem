const {MessageEmbed, MessageActionRow, MessageButton} = require("discord.js");
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
            if(!interaction.options._hoistedOptions[0].value.match(regex)[0]) return interaction.reply({content: "A domain name could not be parsed from the given input.", ephemeral: true})
            const domain = interaction.options._hoistedOptions[0].value.match(regex)[0]
            const inf = await client.phish.phisherman(domain)
            const dns = await client.phish.dnsSearch(`${interaction.options._hoistedOptions[0].value.match(regex)[0]}`)
            /*
            new MessageEmbed()
                     .setColor('RANDOM')
                     .setDescription(dns.domain)
                     .addField("__Whois Server__", dns.whois_server ? dns.whois_server : "No dns server found", true)
                     .addField("__Registrar__", dns.registrar.name ? dns.registrar.name : "No registrar name found.", true)
                     .addField("__Iana ID__", dns.registrar.iana_id ? dns.registrar.iana_id : "No iana ID found.", true)
                     .addField("__Registrant Name__", dns.registrant.name ? dns.registrant.name : "No name found.", true)
                     .addField("__Registrant Organization__", dns.registrant.organization ? dns.registrant.organization : "No organization registered.", true)
                     .addField("__Registrant City__", dns.registrant.city ? dns.registrant.city : "No city registered.", true)
                     .setFooter({
                         text: `Last updated: ${moment(dns.update_date).format("LL")}`,
                         iconURL: interaction.member.avatarURL({dynamic: true})
                     })
             */

            if(!inf[domain] || inf[domain].classification === 'unknown') return interaction.reply({embeds: [ new MessageEmbed().setColor('RED').setDescription(domain).addField("Classification",  "❓ Unknown").addField("__Whois Server__", dns.whois_server ? dns.whois_server : "No dns server found", true)
                    .addField("__Registrar__", dns.registrar.name ? dns.registrar.name : "No registrar name found.", true)
                    .addField("__Iana ID__", dns.registrar.iana_id ? dns.registrar.iana_id : "No iana ID found.", true)
                    .addField("__Registrant Name__", dns.registrant.name ? dns.registrant.name : "No name found.", true)
                    .addField("__Registrant Organization__", dns.registrant.organization ? dns.registrant.organization : "No organization registered.", true)
                    .addField("__Registrant City__", dns.registrant.city ? dns.registrant.city : "No city registered.", true)
                    .setFooter({
                        text: `Last updated: ${moment(dns.update_date).format("LL")}`,
                        iconURL: interaction.member.avatarURL({dynamic: true})
                    })]})
            if(inf[domain].classification === 'safe') return interaction.reply({embeds: [new MessageEmbed().setDescription(domain).setColor("GREEN").addField('Classification', '<:2585modshieldlightgreenicon:927289585761927168> Safe').addField("__Whois Server__", dns.whois_server ? dns.whois_server : "No dns server found", true)
                    .addField("__Registrar__", dns.registrar.name ? dns.registrar.name : "No registrar name found.", true)
                    .addField("__Iana ID__", dns.registrar.iana_id ? dns.registrar.iana_id : "No iana ID found.", true)
                    .addField("__Registrant Name__", dns.registrant.name ? dns.registrant.name : "No name found.", true)
                    .addField("__Registrant Organization__", dns.registrant.organization ? dns.registrant.organization : "No organization registered.", true)
                    .addField("__Registrant City__", dns.registrant.city ? dns.registrant.city : "No city registered.", true)
                    .setFooter({
                        text: `Last updated: ${moment(dns.update_date).format("LL")}`,
                        iconURL: interaction.member.avatarURL({dynamic: true})
                    }) ]})
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
                classification = "<:2189modshieldyellowicon:929213568535117884> Suspicious"
            } else if(classification === 'malicious') {
                embed.setColor('RED')
                classification = "<:image_20211228_114840:925475350706806875> Malicious"
            }

            let firstSeen = inf[`${domain}`].firstSeen
            if(!firstSeen) firstSeen = Date.now()

            let lastSeen = inf[`${domain}`].lastSeen
            if(!lastSeen) lastSeen = Date.now()
            const urlscan = new MessageActionRow()
                .addComponents(new MessageButton()
                    .setURL(`https://urlscan.io/result/${inf[`${domain}`].details.urlScanId}`)
                    .setLabel('UrlScan')
                    .setEmoji('🛠️')
                    .setStyle(5),
                )
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

            return interaction.reply({embeds: [embed], components: [urlscan]})

        } catch(e) {
            console.log(e)
            return interaction.reply({content: "Unable to get information on that domain, try again in one minute.", ephemeral: true})
        }
    }
}