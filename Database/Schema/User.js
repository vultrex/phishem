const mongoose = require("mongoose");

module.exports = mongoose.model("User", new mongoose.Schema({
   user_id: {type: String, default: null},
    user_warnings: {type: Number, default: 0},
}))