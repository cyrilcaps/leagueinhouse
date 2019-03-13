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
        .then(res => this.setState({response: res.data}))
        .catch(err => console.log(err));
  }
  callApi = async () => {
    const response = await fetch('/api/overview');
    const body = await response.json();
    if (response.status !== 200) throw Error(body.message);
    return body;
  };
  handleSubmit = async e => {
    e.preventDefault();
    const response = await fetch('/api/world', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({post: this.state.post}),
    });
    const body = await response.text();
    this.setState({responseToPost: body});
  };
  render() {
    return (<div>{this.state.response}</div>);
  }
}
export default App;