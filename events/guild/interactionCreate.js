const Timeout = new Set()
const { MessageEmbed } = require('discord.js');
const humanizeDuration = require("humanize-duration");

module.exports = async(client, interaction) => {
	if (interaction.isCommand() || interaction.isContextMenu()) {
		if (!client.slash.has(interaction.commandName)) return;
		if (!interaction.guild) return interaction.reply({content: "Slash commands can only be used in a server."});
		const command = client.slash.get(interaction.commandName)
		try {

			if (command.timeout) {
				if (Timeout.has(`${interaction.user.id}${command.name}`)) {
					const embed = new MessageEmbed()
						.setTitle('You are in timeout!')
						.setDescription(`You need to wait **${humanizeDuration(command.timeout, {round: true})}** to use command again`)
						.setColor('#ff0000')
					return interaction.reply({embeds: [embed], ephemeral: true})
				}
			}
			if (command.permissions) {
				if (!interaction.member.permissions.has(command.permissions)) {
					const embed = new MessageEmbed()
						.setTitle('You\'re missing permissions!')
						.setThumbnail(interaction.member.user.avatarURL({dynamic: true}))
						.setDescription(`<:3595failed:926715200172867624> You need \`${command.permissions}\` to use this command`)
						.setColor('#ff0000')
						.setTimestamp()
					return interaction.reply({embeds: [embed], ephemeral: true})
				}
			}

			command.run(interaction, client);
			Timeout.add(`${interaction.user.id}${command.name}`)
			setTimeout(() => {
				Timeout.delete(`${interaction.user.id}${command.name}`)
			}, command.timeout);
		} catch (error) {
			console.error(error);
			await interaction.reply({content: ':x: There was an error while executing this command!', ephemeral: true});
		}

	}
} 