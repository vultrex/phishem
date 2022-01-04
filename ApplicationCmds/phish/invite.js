module.exports = {
    name: "invite",
    description: "Get Phishem's invite link",
    options: [],
    category: "phish",
    run: async(interaction, client) => {
        interaction.reply({content: `https://nek.wtf/phish/invite`})
    }
}