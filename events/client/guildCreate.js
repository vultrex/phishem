module.exports = async (client, guild) => {
    client.db.set(`${guild.id}.config.delete`, true)
    await require(`../../slash.js`)()
}