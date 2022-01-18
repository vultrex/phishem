const mongoose = require("mongoose");

module.exports = mongoose.model("Guild", new mongoose.Schema({

    id: { type: String }, //ID of the guild
    name: { type: String }, //Name of the guild
    // Logger
    config: {
        delete: { type: Boolean, default: true }, //Delete the guild after the bot is restarted
        youtube_filter: { type: Boolean, default: false }, //Filter youtube links
        ignore_staff: { type: Boolean, default: false }, //Ignore staff members
        bypass: [{type: String, default: ""}], //Bypass the filter
        action_ban: { type: Boolean, default: false }, //Ban the user after an action
        action_kick: { type: Boolean, default: false }, //Kick the user after an action
        action_timeout: { type: Boolean, default: false }, //Mute the user after an action
    },
    log: {
        webhookID: { type: String, default: null }, //ID of the webhook
        webhookToken: { type: String, default: null }, //Token of the webhook
        webhookChannelID: { type: String, default: null }, //ID of the channel the webhook is in
    }



}));