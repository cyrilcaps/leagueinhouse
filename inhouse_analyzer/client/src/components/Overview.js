import '../App.css';

import React, {Component} from 'react';
import SummonerProfiles from './OverviewProfiles';

class Overview extends Component {
  constructor(props) {
    super();
  }

  render() {
    let d = this.props.data;
    var elements = [];
    if (typeof (d) == 'object') {
      for (var summoner in d['summoners']) {
        let dataToPass = {summoner: d['summoners'][summoner]};
        elements.push(<SummonerProfiles data = {
          dataToPass
        } />);
      }
    }
    return (<div className="dataContainer">{elements}</div>)
      }
    }


    export default Overview;
