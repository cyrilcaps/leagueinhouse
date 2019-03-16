import './App.css';

import React, {Component} from 'react';

import logo from './logo.svg';

class App extends Component {
  state = {
    response: '',
    post: '',
    responseToPost: '',
  };
  componentDidMount() {
    this.callApi()
        .then(res => this.setState({response: res.express}))
        .catch(err => console.log(err));
  }
  callApi = async () => {
    const response = await fetch('/api/overview');
    const body = await response.json();
    if (response.status !== 200) throw Error(body.message);
    return body;
  };

  render() {
    return (<div>hello world</div>);
  }
}

export default App;