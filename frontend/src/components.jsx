import React from 'react';
import { useParams, Link } from "react-router-dom";
import { useQuery } from '@apollo/react-hooks';
import Nav from 'react-bootstrap/Nav';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';

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

function Metadata({ inner }) {
    return <div><pre>{JSON.stringify(inner, null, 2)}</pre></div>
}


function SKURows() {
    const { loading, error, data } = useQuery(SKUS, { variables: useParams() });

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error :(</p>;

    return data.skus.edges.map(({ node }) => (
        <SKURow node={node}></SKURow>
    ));
}


function Home() {
    return <div class="jumbotron">crusher.beta</div>
}

export { Clients, Contacts, Metadata, SKUs, Home, MainNav };


function MainNav() {
    return <Nav fill variant="pills" activeKey={"/" + window.location.pathname.split("/")[1]}>
        <Nav.Item>
            <Nav.Link href="/">Home</Nav.Link>
        </Nav.Item>
        <Nav.Item>
            <Nav.Link href="/skus">SKUs</Nav.Link>
        </Nav.Item>
        <Nav.Item>
            <Nav.Link href="/contacts">Contacts</Nav.Link>
        </Nav.Item>
        <Nav.Item>
            <Nav.Link href="/clients">Clients</Nav.Link>
        </Nav.Item>
    </Nav>;
}

function SKUs() {
    return <Table striped bordered hover>
        <thead>
            <tr>
                <th>SKU ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Units</th>
                <th>Default Price</th>
                <th>Default Quantity</th>
                <th>Minimum Quantity</th>
                <th>Maximum Quantity</th>
                <th>Minimum Price</th>
                <th>Maximum Price</th>
                <th>Metadata</th>
                <th>Actions</th>
            </tr>
        </thead>
        <SKURows></SKURows>
    </Table>
}

function SKURow({ node }) {
    return <tr>
        <td>{node.skuId}</td>
        <td>{node.name || node.metadata.name || "???"}</td>
        <td>{node.type}</td>
        <td>{node.units}</td>
        <td>{node.defaultPrice}</td>
        <td>{node.defaultQuantity}</td>
        <td>{node.minimumQuantity}</td>
        <td>{node.maximumQuantity}</td>
        <td>{node.minimumPrice}</td>
        <td>{node.maximumPrice}</td>
        <td><Metadata inner={node.metadata}></Metadata></td>
        <td><ButtonGroup><Button variant="danger">Delete</Button><Button varian="info">Edit</Button></ButtonGroup></td>
    </tr>
}
