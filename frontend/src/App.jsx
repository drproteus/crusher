import React, { Fragment } from 'react';
import ReactDOM from 'react-dom';

import { ApolloProvider } from '@apollo/react-hooks';
import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client';


import { useQuery } from '@apollo/react-hooks';

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
import { gql } from 'apollo-boost';

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
      <h2>My first Apollo app 🚀</h2>
    </div>

    <GetClients />
  </ApolloProvider>
);

ReactDOM.render(<App />, document.getElementById('root'));



function GetClients() {
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
