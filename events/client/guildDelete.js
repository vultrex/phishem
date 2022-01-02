module.exports = async (client, guild) => {
    client.db.delete(`${guild.id}.config.delete`)
    client.db.delete(`${guild.id}.config.log.channelId`)
    client.db.delete(`${guild.id}.config.log.id`)
    client.db.delete(`${guild.id}.config.log.token`)
    client.db.delete(`${guild.id}.config.youtube`)
    client.db.delete(`${guild.id}.config.ban`)
    client.db.delete(`${guild.id}.config.kick`)
    client.db.delete(`${guild.id}.config.timeout`)
}