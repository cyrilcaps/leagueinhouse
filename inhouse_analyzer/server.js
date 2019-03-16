const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 5000;
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

var overviewData = require('./overview_data/season_2.json');

app.get('/api/overview', (req, res) => {
  res.send(overviewData);
});

app.listen(port, () => console.log(`Listening on port ${port}`));