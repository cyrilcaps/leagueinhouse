import '../App.css';
import React, {Component} from 'react';

const importAll = require => require.keys().reduce((acc, next) => {
  acc[next.replace('./', '')] = require(next);
  return acc;
}, {});

const images =
    importAll(require.context('./images/champion_squares', false, /\.(png)$/));

console.log(images);
class SummonerProfiles extends Component {
  constructor(props) {
    super();
  };

  render() {
    let d = this.props['data']['summoner'];
    var summoner = d['summoner'], won = d['won'], lost = d['lost'],
        g_p = d['games played'], champs = d['most played champs'],
        roles = d['most played roles'], winRate = d['win rate'];

    var champ_list = [];
    for (var i in champs) {
      let source = champs[i][0] + '.png'
      champ_list.push(<img className = 'Ochamps' src={images[source]}></img>)
      if (champ_list.length > 2) {
        break;
      }
    }

    var role_list = [];
    for (var k in roles) {
      role_list.push(roles[k][0]);
      if (role_list.length > 2) {
        break;
      }
    }


    return (
        <div className = 'userProfiles'><div className = 'OsummName'>{summoner}<
            /div>
        <div className = 'Orecord'>Won : {won}<br></br>Lost:
            {lost}<br>
        </br> Win Rate:
                    {winRate}<br></br>Roles:
            {role_list.toString().toLowerCase()}<
                /div>
            <div className = 'divChamps'>Played Champs:<br></br>{[champ_list]}</div>
  < /div>)
  }
}

export default SummonerProfiles;