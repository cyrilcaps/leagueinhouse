import '../App.css';

import React, {Component} from 'react';

class SummonerProfiles extends Component {
  constructor(props) {
    super();
  };

  render() {
    let d = this.props['data']['summoner'];
    console.log(d)
    return (<div className = 'userProfiles'><div className = 'OsummName'>{
        d['summoner']}<
            /div>
        <div className = 'Orecord'>Won : {d['won']}<br></br>
                Lost: {d['lost']}<br>
            </br>Games played: {d['games played']}<br></br>Win Rate:
                {d['win rate']}</div>
        </div>)
  }
}

export default SummonerProfiles;