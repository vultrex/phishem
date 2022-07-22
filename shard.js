const {ShardingManager} = require("discord.js");
require("dotenv").config();

const manager = new ShardingManager("./index.js", {
    token: process.env.TOKEN,
    autoSpawn: true,
    respawn: true,
});

require("colors");
manager.on("shardCreate", (shard) => {
    console.log(`Sharding Manager: `.green + `Launched shard #${shard.id}\n─────────────────────────────── `);
});

manager.spawn({amount: "auto", delay: undefined, timeout: -1});

