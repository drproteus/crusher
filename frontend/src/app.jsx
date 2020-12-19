import React, { Fragment } from 'react';
import ReactDOM from 'react-dom';

import Container from 'react-bootstrap/Container';

import { ApolloProvider } from '@apollo/react-hooks';
import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client';

import { SKUs, Clients, Contacts, Home, MainNav } from "./components.jsx";

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
    <Router>
      <Container fluid className="p-3">
        <h2>CRUSHER 🚀</h2>
        <MainNav></MainNav>
        <Container fluid className="p-3">
          <Switch>
            <Route path="/skus/by-type/:skuType">
              <h3>SKUs by Type</h3>
              <SKUs />
            </Route>
            <Route path="/skus/by-tag/:tag">
              <h3>SKUs by Tag</h3>
              <SKUs />
            </Route>
            <Route path="/skus/:id">
              <SKUs />
            </Route>
            <Route path="/skus">
              <h3>All SKUs</h3>
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
        </Container>
      </Container>
    </Router>
  </ApolloProvider>
);

ReactDOM.render(<App />, document.getElementById('root'));
