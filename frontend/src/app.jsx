import React, { Fragment } from 'react';
import ReactDOM from 'react-dom';

import { ApolloProvider } from '@apollo/react-hooks';
import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client';

import { SKUs, Clients, Contacts, Home } from "./components.jsx";

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useParams
} from "react-router-dom";


const link = createHttpLink({
  uri: '/graphql',
  credentials: 'same-origin',
  headers: {
    'X-CSRFToken': document.querySelector("input[name=csrfmiddlewaretoken]").value
  }
});

const client = new ApolloClient({
  cache: new InMemoryCache(),
  link,
});

const App = () => (
  <ApolloProvider client={client}>
    <div>
      <h2>CRUSHER 🚀</h2>
    </div>
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/skus">SKUs</Link>
            </li>
            <li>
              <Link to="/contacts">Contacts</Link>
            </li>
            <li>
              <Link to="/clients">Clients</Link>
            </li>
          </ul>
        </nav>

        <Switch>
          <Route path="/skus/by-type/:skuType">
            <SKUs />
          </Route>
          <Route path="/skus/by-tag/:tag">
            <SKUs />
          </Route>
          <Route path="/skus/:id">
            <SKUs />
          </Route>
          <Route path="/skus">
            <SKUs />
          </Route>
          <Route path="/contacts/:id">
            <Contacts />
          </Route>
          <Route path="/contacts">
            <Contacts />
          </Route>
          <Route path="/clients/:id">
            <Clients />
          </Route>
          <Route path="/clients">
            <Clients />
          </Route>
          <Route path="/">
            <Home />
          </Route>
        </Switch>
      </div>
    </Router>
  </ApolloProvider>
);

ReactDOM.render(<App />, document.getElementById('root'));
