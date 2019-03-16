import './App.css';

import React, {Component} from 'react';

class App extends Component {
  state = {
    response: '',
    post: '',
    responseToPost: '',
    active: 'overview',
    summoners: false,
    overview: true,
    champions: false
  };
  componentDidMount() {
    this.callApi()
        .then(res => this.setState({response: res}))
        .catch(err => console.log(err));
  }
  callApi = async () => {
    const response = await fetch('/api/overview');
    const body = await response.json();
    if (response.status !== 200) throw Error(body.message);
    return body;
  };

  activateState(e) {
    let activeState = e.target.text.toLowerCase();
    let newState = {active: activeState};
    let states = ['summoners', 'champions', 'overview'];
    for (var i in states) {
      if (activeState === states[i]) {
        newState[states[i]] = true;
      } else {
        newState[states[i]] = false;
      }
    }
    this.setState(newState)
  };

  render() {
    let oClass = this.state.overview ? 'active' : '';
    let sClass = this.state.summoners ? 'active' : '';
    let cClass = this.state.champions ? 'active' : '';
    return (
        <div className = 'test'><ul className = 'navbar'><li>
        <a className = {oClass} href = '#' onClick = {this.activateState.bind(
             this)}>Overview</a>
        </li><li>
        <a className = {sClass} href = '#Summoners' onClick =
             {this.activateState.bind(this)}>Summoners</a>
        </li><li>
        <a className = {cClass} href = '#Champions' onClick =
             {this.activateState.bind(this)}>Champions</a>
        </li>
        </ul></div>);
  }
}


class Overview extends Component {}
export default App;