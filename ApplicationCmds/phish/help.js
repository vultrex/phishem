const Discord = require("discord.js");
module.exports = {
    name: "help",
    description: "Not exactly a help command but it's here if you need it.",
    options: [],
    category: "phish",
    run: async(interaction, client) => {
        return interaction.reply({embeds: [

                new Discord.MessageEmbed()
                    .setColor(2201842)
                    .setAuthor({
                        name: client.user.username,
                        iconURL: client.user.displayAvatarURL({ format: 'png'})
                    })
                    .setDescription("Phishem - Another advanced phish detection bot with YouTube video filtering.\n\nUpon inviting Phishem to your server, auto deletion of the filters are automatically enabled, but you can enable more functions and configurations with the provided slash commands. \n**Note** that by default, users with the permissions: `MANAGE_GUILD`, `MANAGE_MESSAGES`, and `MODERATE_MEMBERS` will be automatically ignored. \n\n__Slash Information__: \n```bash\n/configure get \"Gets your server's current configurations settings, saying if something is on or off.\"\n\n/search \"Check urls or domains against the phishing databases.\"\n\n/configure bypass url\n-----add \"Add links that will be ignored by the filters.\"\n-----remove \"Delete a bypass link which will no longer be ignored.\"\n\n/configure set \n-----delete \"Either enable or disable message deletion upon a positive detection\" \n-----youtube-filter \"Either enable or disable YouTube video filtering for fake nitro generator videos.\"\n-----log \"Set your log channel to get notifications if a phishing or malicious is found.\"\n-----action \"Enable if the bot is either going to ban, kick, or timeout the user when a filter gets triggered.\"\n\n/configure reset \n-----configurations \"Show all the server configurations to reset\"\n---------Delete \"Disables message deletion.\"\n---------YouTube-filter \"Disable YouTube filtering.\" \n---------Log \"Disables logging and delete the logger webhook from the channel.\"\n---------Actions \"Disables all the actions.\"\n---------All \"Disables and resets all the configurations.\" \n```\n\n**[Private Policy](https://github.com/Ne-k/Docs/blob/main/Phishem/Readme.md)** | **[Invite](https://nek.wtf/phish/invite)**")


            ]})
    }
}
