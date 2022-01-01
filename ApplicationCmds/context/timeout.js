const {Permissions} = require('discord.js')
module.exports = {
    name: "timeout-user",
    permissions: "MODERATE_MEMBERS",
    type: 3,
    run: async(interaction, client) => {
        try {


        const message = interaction.options.getMessage('message');
        if(!message.guild.me.permissions.has(Permissions.FLAGS.MODERATE_MEMBERS)) return interaction.reply({content: 'I need `MODERATE_MEMBERS` to timeout users.', ephemeral: true})
            if(message.member.isCommunicationDisabled()) return interaction.reply({content: 'User has already been timed out.', ephemeral: true})
        await message.member.timeout(1000 * 60 * 1000, `Timed out by ${interaction.member.user.tag}`).catch(e => {
            return interaction.reply(`Looks like there was an issue with timing out the user.`, {ephemeral: true})
        })
        interaction.reply({content: `${message.author.tag} has been timed out for 16 hours.`, ephemeral: true})
        } catch (e) {
            return interaction.reply({content: `Looks like something odd happened when attempting to time out the user, try again later.`, ephemeral: true})
        }
    }
    }