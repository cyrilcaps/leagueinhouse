import './App.css';

import React, {Component} from 'react';

class App extends Component {
  state = {
    response: '',
    post: '',
    responseToPost: '',
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

  render() {
    return (<NavBar />);
  }
}

class NavBar extends Component {
  state = {active: 'overview'};

  render() {
    return (<div className = 'nav'><ul className = 'navbar'><li>
            <a href = '#'>Overview</a></li><li>
            <a href = '#Summoners'>Summoners</a></li><li>
            <a href = '#Champions'>Champions</a></li></ul></div>);
  };
}
export default App;