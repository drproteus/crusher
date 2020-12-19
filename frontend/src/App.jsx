import React, { Fragment } from 'react';
import ReactDOM from 'react-dom';

import { ApolloProvider } from '@apollo/react-hooks';
import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useParams
} from "react-router-dom";


import { useQuery } from '@apollo/react-hooks';
import { gql } from 'apollo-boost';


const CLIENTS = gql`
{
  clients {
    edges {
      node {
        clientId,
        company,
        contact {
          id,
          name,
          primaryEmail
        }
      }
    }
  }
}
`

const CONTACTS = gql`{contacts{edges{node{contactId,name}}}}`;
const SKUS = gql`{skus{edges{node{skuId,metadata,defaultPrice,defaultQuantity}}}}`;

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
          </ul>
        </nav>

        {/* A <Switch> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
        <Switch>
          <Route path="/skus">
            <SKUs />
          </Route>
          <Route path="/contacts/:id">
            <Contact />
          </Route>
          <Route path="/contacts">
            <Contacts />
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


function Clients() {
  const { loading, error, data } = useQuery(CLIENTS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  return data.clients.edges.map(({ node }) => (
    <div key={node.clientId}>
      <p>
        {node.company}: {node.clientId}
      </p>
    </div>
  ));
}


function Contacts() {
  const { loading, error, data } = useQuery(CONTACTS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  return data.contacts.edges.map(({ node }) => (
    <div key={node.contactId}>
      <p>
        {node.name}: <Link to={`/contacts/${node.contactId}`}>{node.contactId}</Link>
      </p>
    </div>
  ));
}

function Contact() {
  let contactId = useParams().id;
  const { loading, error, data } = useQuery(gql`query{contact(id: "${contactId}"){id,metadata,fullname,}}`);
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  return <div>
    <h2>{data.contact.fullname}</h2>
    <Metadata inner={data.contact.metadata}></Metadata>
  </div>;
}

function Metadata(data) {
  return <div><pre>{JSON.stringify(data.inner, null, 2)}</pre></div>
}


function SKUs() {
  const { loading, error, data } = useQuery(SKUS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  return data.skus.edges.map(({ node }) => (
    <div key={node.contactId}>
      <p>
        {node.name}
      </p>
    </div>
  ));
}


function Home() {
  return <div class="jumbotron">crusher.beta</div>
}
