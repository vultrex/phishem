module.exports = {
    name: "support",
    description: "Get the invite for the support server.",
    options: [],
    category: "phish",
    run: async(interaction, client) => {
        interaction.reply({content: `https://nek.wtf/phish/invite`})
    }
}