const {MessageEmbed, WebhookClient, Message} = require('discord.js');
const fetch = require('node-fetch');
const moment = require("moment");
module.exports = {
    name: "userinfo",
    description: "Get information about a user.",
    options: [
        {
            name: "user",
            description: "The user to get information about.",
            required: true,
            type: 3
        }

    ],
    category: "phish",
    run: async (interaction, client) => {
       try {
           const user = interaction.options._hoistedOptions[0].value
           if(!isNaN(user)) {
               const globaluser = await client.users.fetch(user)
               if(!globaluser) {
                   return interaction.reply({content: "User not found.", ephemeral: true})
               }
               let us = await fetch(`https://japi.rest/discord/v1/user/${(await globaluser).id}`).then(res => res.json())
               let banner = us.data.bannerURL
               if(!banner) {
                   banner = "https://media.discordapp.net/attachments/854794095066349618/934669695859191848/unknown.png"
               } else {
                   banner = us.data.bannerURL + '?size=2048'
               }
               let flags = us.data.public_flags_array.join(' | ')
               if(flags.length > 100) {
                   flags = "User has too many flags to display."
               }
               if(!flags) {
                   flags = "User has no flags, or I can't find them."
               }
               return interaction.reply({
                   embeds: [
                       new MessageEmbed()
                           .setURL(`https://discord.com/users/${user}`)
                           .setTitle(`${(await globaluser).username}#${(await globaluser).discriminator} | ${(await globaluser).id}`)
                           .setDescription(`**Bot**: \`${(await globaluser).bot}\`\n**Created at**: \`${require('moment')((await globaluser).createdAt).format('LLL')}\` (<t:${require('moment')((await globaluser).createdAt).format('X')}:R>)\n**User flags** \`${flags}\``)
                           .setThumbnail((await globaluser).displayAvatarURL({ dynamic: true }))
                           .setColor('#0099ff')
                           .setImage(banner)
                   ]
               })
           } else {
               return interaction.reply({content: "Please input a user ID.", ephemeral: true})
           }
       } catch (e) {
           const webhook = new WebhookClient({
               id: "941217050871877704",
               token: "Wg2_6F6jjnESXM4HcPwqtCAbZ7dbnxkDt4gI8-RxXGESp0gjpdPVkh9ZWOkhRW8HCM-Z"
           });

          await webhook.send({
               embeds: [
                   new MessageEmbed().setTitle("An error occurred:").setDescription(`\`\`\`${e}\`\`\``).setColor('RED')
               ]
           })
           return await interaction.reply({content: "An error occurred, the ID you provided might be an invalid user.", ephemeral: true})
       }
    }
}