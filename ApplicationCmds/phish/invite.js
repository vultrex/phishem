module.exports = {
    name: "invite",
    description: "Get Phishem's invite link",
    options: [],
    category: "phish",
    run: async(interaction, client) => {
        interaction.reply({content: `https://discord.com/oauth2/authorize?client_id=926687914174341130&scope=bot+applications.commands&permissions=1377342712950`})
    }
}