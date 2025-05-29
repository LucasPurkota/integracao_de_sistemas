const express = require('express');
const redis = require('redis');

const app = express();
app.use(express.json());

const redisClient = redis.createClient({
  url: 'redis://localhost:6379'
});

redisClient.on('error', (err) => {
  console.error('Erro no redis', err);
});

(async () => {
  await redisClient.connect();
  console.log('Conectado ao Redis');
})();

const sensorData = [
    { temparatura: 25, pressao: 10.2},
    { temparatura: 26, pressao: 11.0 },
    { temparatura: 14, pressao: 5.4 }
  ];

app.get('/sensor-data', async(req, res) => {
  try {
    const cache = await redisClient.get('sensorData');
    
    if (cache) {
      console.log('Dados retornados do redis');
      return res.json(JSON.parse(cache));
    }
    
    await redisClient.setEx('sensorData', 30, JSON.stringify(sensorData));
    
    console.log('Dados retornados da lista');
    
    res.json(sensorData);
  } catch (err) {
    res.status(500).json({ error: 'Erro ao acessar Redis' });
  }
});

app.post('/alert', async (req, res) => {
  const { temperatura, pressao } = req.body;

  if (temperatura > 30 || pressao < 5) {
    return res.status(200).json({ message: 'As condições estão fora do normal' });
  }

  res.status(200).json({ message: 'As condições estão dentro do normal' });
});

app.listen(3000, () => {
  console.log('Servidor rodando na porta 3000');
});