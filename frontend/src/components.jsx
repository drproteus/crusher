import React from 'react';
import { useParams, Link } from "react-router-dom";
import { useQuery } from '@apollo/react-hooks';
import Nav from 'react-bootstrap/Nav';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Media from 'react-bootstrap/Media';
import Alert from 'react-bootstrap/Alert';
import Image from 'react-bootstrap/Image';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import { SKUS, CONTACTS, CLIENTS } from "./queries.jsx";


function ClientDetail({ client }) {
    let details = [
        <Media>
            <ClientImage client={client} width={200} height={200}></ClientImage>
            <Media.Body style={{ marginLeft: 10 }}>
                <h4>{client.company}</h4>
                <p className="text-muted"><Link to={"/clients/" + client.clientId}>{client.clientId}</Link></p>
                <pre>ADD MORE STUFF HERE</pre>
            </Media.Body>
        </Media>,
        <h5>metadata</h5>,
        <Metadata inner={client.metadata}></Metadata>,
        <Row>
            <Col md={6} className="p-3">
                <ClientInvoiceList client={client}></ClientInvoiceList>
            </Col>
            <Col md={6} className="p-3">
                <ClientContactShort client={client}></ClientContactShort>
            </Col>
        </Row>
    ];
    return details;
}

function ClientInvoiceList({ client }) {
    let data = [<h5>Invoices</h5>];
    if (client.invoices.edges.length < 1) {
        data.push(<Alert>no invoices found for client</Alert>);
    } else {
        for (invoice in client.invoices.edges) {
            data.push(invoice.id)
        }
    }
    return data
}

function ClientContactShort({ client }) {
    if (!client.contact) {
        return [];
    }
    return [
        <Alert variant="info">
            <h5>Contact</h5>
            <p>
                {client.contact.primaryEmail}
            </p>
            <p>
                {client.contact.name}
            </p>
            <Link to={"/contacts/" + client.contact.id}><Button>View</Button></Link>
        </Alert>
    ];
}

function Clients() {
    const { loading, error, data } = useQuery(CLIENTS, { variables: useParams() });

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error :(</p>;

    return data.clients.edges.map(({ node }) => (
        <div key={node.clientId}>
            <ClientDetail client={node}></ClientDetail>
        </div>
    ));
}

function ClientImage({ client, width, height }) {
    let placeholder = client.metadata.profile_image_url || "http://placekitten.com/200/200";
    return <Image width={width} height={height} src={placeholder} thumbnail></Image>;
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
    let data = []
    for (var k in inner) {
        if (inner.hasOwnProperty(k)) {
            data.push(
                <tr><th>{k}</th><td>{JSON.stringify(inner[k])}</td></tr>
            );
        }
    };
    if (data.length < 1) {
        return [];
    }
    return [
        <Table size="sm" borderless striped hover>
            <tbody>{data}</tbody>
        </Table>
    ];
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
    return <div className="jumbotron">crusher.beta</div>
}

export { Clients, Contacts, Metadata, SKUs, Home, MainNav };


function MainNav() {
    return <Nav className="flex-column" variant="pills" activeKey={"/" + window.location.pathname.split("/")[1]}>
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
                <th>Name</th>
                <th>Type</th>
                <th>Units</th>
                <th>Default Price</th>
                <th>Default Quantity</th>
            </tr>
        </thead>
        <tbody>
            <SKURows></SKURows>
        </tbody>
        <tfoot></tfoot>
    </Table>
}

function SKURow({ node }) {
    return [
        <tr key={node.skuId}>
            <td>{node.name || node.metadata.name || "???"}</td>
            <td><Link to={"/skus/by-type/" + node.metadata.type}>{node.metadata.type}</Link></td>
            <td>{node.units}</td>
            <td>{node.defaultPrice}</td>
            <td>{node.defaultQuantity}</td>
        </tr>,
        <tr key={"extra-" + node.skuId}>
            <td></td>
            <td><Metadata inner={node.metadata}></Metadata></td>
            <td colSpan="2" align="right"><Link to={`/skus/${node.skuId}`}>{node.skuId}</Link></td>
            <td align="center"><ButtonGroup><Button variant="danger">Delete</Button><Button variant="info">Edit</Button></ButtonGroup></td>
        </tr>
    ]
}
