require('colors')

module.exports = async client => {   
      client.user.setActivity('Phish', { type: 'LISTENING' });
      console.log(`Logged in as ${client.user.tag}`.magenta);
};