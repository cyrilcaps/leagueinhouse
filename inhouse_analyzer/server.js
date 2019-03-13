const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 5000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

var fs = require('fs')
var match_d = './match_data'
var matches = []
app.listen(port, () => console.log(`Listening on port ${port}`));

app.get(
    '/api/overview',
    (req, res) => {
    fs.readdir(match_d, (err, files) => {
  if (err) {
    console.error('Could not list the directory.', err);
    res.send({})
  } else {
    files.forEach(
        (file, index) => {matches.push(require(match_d + '/' + file))})
  }
    })

    res.send({data: 'test'})
  });
