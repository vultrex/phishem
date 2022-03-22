module.exports = {
    name: "support",
    description: "Get the invite for the support server.",
    options: [],
    category: "phish",
    run: async(interaction, client) => {
        interaction.reply({content: `https://discord.gg/yG9N4JABP3`})
    }
    }