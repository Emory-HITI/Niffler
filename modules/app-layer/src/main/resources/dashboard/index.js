var jwt = require('jsonwebtoken');
const express = require('express');
const cookieParser = require('cookie-parser');
const path = require("path");
const bodyParser = require("body-parser");

// env vars
const PASSPHRASE = process.env.PASSPHRASE || "privatefolder"
const PORT = process.env.PORT || 8888
const user_pass_phrase = require('./users.json');
const __password = "NIFFLERisSNAKES"




const getToken = function(req) {

  if (req.headers.authorization &&
    req.headers.authorization.split(' ')[0] === 'Bearer') { // Authorization: Bearer g1jipjgi1ifjioj
    // Handle token presented as a Bearer token in the Authorization header

    return req.headers.authorization.split(' ')[1];

  } else if (req.query && req.query.token) {
    // Handle token presented as URI param

    return req.query.token;
  } else if (req.cookies && req.cookies.token) {
    // Handle token presented as a cookie parameter

    return req.cookies.token;
  }
  return null;
};


const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(cookieParser());


function authCheck(req, res, next){
  const token = getToken(req)
  if (!token) {
    res.redirect('./login.html');
    return;
  }
  jwt.verify(token, user_pass_phrase.JWT_SECRET, function(err, decoded) {
    if (err || decoded.password!==__password) {
      res.redirect('/login.html');
      return;
    };
    next()
  });

}



app.post('/login', function(req, res) {
  var password = req.body.password;
  if (password&&password == __password) {
    const token = jwt.sign( {password : __password}, user_pass_phrase.JWT_SECRET, {expiresIn: 86400});
    res.status(200).send({ auth: true, token: token });
  } else {
    res.status(200).send({ auth: false, token: null });
  }
});

app.get('/logout', function(req, res) {
  res.status(200).send({ auth: false, token: null });
});

// use this static public
app.use(express.static("./static"))

// hold data back
app.use("/data", authCheck)
app.use("/data", express.static(path.join(__dirname, 'data')))


app.listen(PORT, () => console.log('listening on ' + PORT));
