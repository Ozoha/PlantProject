import ComponentTabs  from "./component/tab";
import React from 'react';
import ReactDOM from 'react-dom';

const App = () => (
  <div>
    <h1>Develop</h1>
    <ComponentTabs />
  </div>
);

ReactDOM.render(<App />, document.getElementById('root'));
