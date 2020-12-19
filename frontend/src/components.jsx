import React from 'react';
import { useParams, Link } from "react-router-dom";
import { useQuery } from '@apollo/react-hooks';

import { SKUS, CONTACTS, CLIENTS } from "./queries.jsx";


function Clients() {
  const { loading, error, data } = useQuery(CLIENTS, { variables: useParams() });

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
  const { loading, error, data } = useQuery(CONTACTS, { variables: useParams() });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  return data.contacts.edges.map(({ node }) => (
    <div key={node.contactId}>
      <p>
        {node.fullname}: <Link to={`/contacts/${node.contactId}`}>{node.contactId}</Link>
      </p>
      <Metadata inner={node.metadata}></Metadata>
    </div>
  ));
}

function Metadata(data) {
  return <div><pre>{JSON.stringify(data.inner, null, 2)}</pre></div>
}


function SKUs() {
  const { loading, error, data } = useQuery(SKUS, { variables: useParams() });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  return data.skus.edges.map(({ node }) => (
    <div key={node.skuId}>
      <p><b>${node.defaultPrice}</b> -- {node.name || "unknown"} -- <em>{node.skuId}</em></p>
      <Metadata inner={node.metadata}></Metadata>
    </div>
  ));
}


function Home() {
  return <div class="jumbotron">crusher.beta</div>
}

export {Clients, Contacts, Metadata, SKUs, Home};
