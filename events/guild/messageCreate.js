const Timeout = new Set();
const { MessageEmbed } = require('discord.js')
const humanizeDuration = require("humanize-duration");
const prefix = process.env.prefix
module.exports = async (client , message) => {
    if (message.author.bot) return;
    if (!message.member) message.member = await message.guild.members.fetch(message.member.id);
    if (!message.guild) return;

   if(new RegExp(/(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]?/gi)) {

       const bitData = await client.phish.checkLink(message.content)

       if(bitData.match) {
           message.delete()

           const phisherman = await client.phish.linkInfo(bitData.matches.map(m => m.domain))

           let linkStatus = phisherman[`${bitData.matches.map(m => m.domain)}`].status

           if (linkStatus === "ONLINE") {
               linkStatus = "Active"
           } else {
               linkStatus = "Inactive"
           }


       } else {
           /*
           const linkTest = new RegExp(/(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?/gi)
           if(linkTest.test(message.content)) {
               const ytLink = new RegExp(/(https?:\/\/[^\s]+)/g)
               if(await client.phish.checkYoutube(message.content.match(ytLink)[0])) {
                   return message.channel.send({content: 'Potential scam youtube video'})
               } else {
                   return
               }


           }
 */
       }
   }

    if (!message.content.toLowerCase().startsWith(prefix)) return;
    const args = message.content.slice(prefix.length).trim().split(/ +/g);
    const cmd = args.shift().toLowerCase();
    if (cmd.length === 0) return; 
    const command = client.commands.get(cmd) || client.commands.find((x) => x.aliases && x.aliases.includes(cmd));
    if (command) {
        if (command.timeout) {
            if (Timeout.has(`${message.author.id}${command.name}`)) {
                const embed = new MessageEmbed()
                .setTitle('You are in timeout!')
                .setDescription(`:x: You need to wait **${humanizeDuration(command.timeout, { round: true })}** to use command again`)
                .setColor('#ff0000')
                return message.channel.send({ embeds: [embed] })
            } else {
                command.run(client, message, args);
                Timeout.add(`${message.author.id}${command.name}`)
                setTimeout(() => {
                    Timeout.delete(`${message.author.id}${command.name}`)
                }, command.timeout);
            }
        } else {
            command.run(client, message, args)
        }
    }
}