const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

const JWT_SECRET = 'ashdjhfoiasahogahehaosidhjas';

const users = [
  {id: 1, email: 'email1@email.com', password: 'senha1', cpf: 'xxx.xxx.xxx-xx'},
  {id: 2, email: 'email2@email.com', password: 'senha2', cpf: 'yyy.yyy.yyy-yy'},
  {id: 3, email: 'email3@email.com', password: 'senha3', cpf: 'kkk.kkk.kkk-kk'},
]

app.post('/login', (req, res) => {
  const {email, password} = req.body;

  const user = users.find(e => e.email == email && e.password == password);

  if (!user) {
    res.status(404).json({msg:"not found"});
  }

  const jwtObject = {
    id: user.id,
    email: user.email,
    password: user.password,
  }

  const token = jwt.sign(jwtObject, JWT_SECRET, {expiresIn: '1s'});

  res.json({token});
});

app.get('/cpf', (req, res) => {
  let token = req.headers.authorization;

  if (!token) res.status(401).json({msg: "token not found"});

  token = token.split(' ')[1];
  
  jwt.verify(token, JWT_SECRET, (err, userJwtToken) =>{
    if (err) res.status(403).json({msg: "invalid token"});
    
    const userSelected = users.find(e => e.id == req.query.id);
    const conditionOfId = userJwtToken.id == userSelected.id;
    const conditionOfUser = userJwtToken.email == userSelected.email;
    const conditionOfPassword = userJwtToken.password == userSelected.password;

    const generalCondition = conditionOfId && conditionOfUser && conditionOfPassword;

    if (!generalCondition) res.status(403).json({msg: "not valid"});

    res.json({cpf: userSelected.cpf});
  });
});

app.listen(3000, () => {
  console.log('Server is up on 3000');
});