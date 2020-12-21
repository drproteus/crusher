import React, { Fragment } from "react";
import ReactDOM from "react-dom";

import Container from "react-bootstrap/Container";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";
import Breadcrumb from "react-bootstrap/Breadcrumb";

import { Icon, InlineIcon } from "@iconify/react";
import shipIcon from "@iconify-icons/uil/ship";
import priceTagAlt from "@iconify-icons/uil/pricetag-alt";

import { ApolloProvider } from "@apollo/react-hooks";
import { ApolloClient, createHttpLink, InMemoryCache } from "@apollo/client";

import { SKUs, Clients, Contacts, Home, MainNav } from "./components.jsx";

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useParams,
} from "react-router-dom";
import { CreateClient } from "./forms.jsx";

const link = createHttpLink({
  uri: "/graphql",
  credentials: "same-origin",
  headers: {
    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]")
      .value,
  },
});

const client = new ApolloClient({
  cache: new InMemoryCache(),
  link,
});

const App = () => (
  <ApolloProvider client={client}>
    <Router>
      <Container>
        <h2>
          <InlineIcon icon={shipIcon}> </InlineIcon>crusher.beta
        </h2>
        <Row>
          <Col md={2}>
            <MainNav></MainNav>
          </Col>
          <Col>
            <Switch>
              <Route path="/skus/by-type/:skuType">
                <SKUs />
              </Route>
              <Route path="/skus/by-tag/:tag">
                <SKUs />
              </Route>
              <Route path="/skus/:uid">
                <SKUs />
              </Route>
              <Route path="/skus">
                <SKUs />
              </Route>
              <Route path="/contacts/:uid">
                <Contacts />
              </Route>
              <Route path="/contacts">
                <Contacts />
              </Route>
              <Route path="/clients/new">
                <CreateClient />
              </Route>
              <Route path="/clients/:uid">
                <Clients />
              </Route>
              <Route path="/clients">
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
  </ApolloProvider>
);

ReactDOM.render(<App />, document.getElementById("root"));
