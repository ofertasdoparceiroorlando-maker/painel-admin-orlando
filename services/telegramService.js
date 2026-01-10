const axios = require("axios");

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

async function enviarMensagem(mensagem) {
  try {
    await axios.post(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
      chat_id: TELEGRAM_CHAT_ID,
      text: mensagem,
      parse_mode: "Markdown"
    });
    console.log("Mensagem enviada ao Telegram com sucesso!");
  } catch (error) {
    console.error("Erro ao enviar mensagem ao Telegram:", error.response?.data || error.message);
  }
}

module.exports = { enviarMensagem };
