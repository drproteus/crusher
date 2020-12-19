import React, { Fragment } from 'react';
import ReactDOM from 'react-dom';

import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

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
      <Container fluid>
        <h2>CRUSHER 🚀</h2>
        <Row>
          <Col md={2}><MainNav></MainNav></Col>
          <Col>
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
                <h3>SKU Detail</h3>
                <SKUs />
              </Route>
              <Route path="/skus">
                <h3>All SKUs</h3>
                <SKUs />
              </Route>
              <Route path="/contacts/:id">
                <h3>Contact Detail</h3>
                <Contacts />
              </Route>
              <Route path="/contacts">
                <h3>All Contacts</h3>
                <Contacts />
              </Route>
              <Route path="/clients/:id">
                <h3>Client Detail</h3>
                <Clients />
              </Route>
              <Route path="/clients">
                <h3>All Clients</h3>
                <Clients />
              </Route>
              <Route path="/">
                <Home />
              </Route>
            </Switch>
          </Col>
        </Row>
      </Container>
    </Router>
  </ApolloProvider >
);

ReactDOM.render(<App />, document.getElementById('root'));
