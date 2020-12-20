import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@apollo/react-hooks";
import Nav from "react-bootstrap/Nav";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Media from "react-bootstrap/Media";
import Alert from "react-bootstrap/Alert";
import Image from "react-bootstrap/Image";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Spinner from "react-bootstrap/Spinner";
import Breadcrumb from "react-bootstrap/Breadcrumb";

import { Icon, InlineIcon } from "@iconify/react";
import shipIcon from "@iconify-icons/uil/ship";
import priceTagAlt from "@iconify-icons/uil/pricetag-alt";
import homeAlt from "@iconify-icons/uil/home-alt";
import suitcaseIcon from "@iconify-icons/uil/suitcase";
import userIcon from "@iconify-icons/uil/user";
import dollarSign from "@iconify-icons/uil/dollar-sign";
import commentAlt from "@iconify-icons/uil/comment-alt";
import wrenchIcon from "@iconify-icons/uil/wrench";
import yinYang from "@iconify-icons/uil/yin-yang";
import ambulanceIcon from "@iconify-icons/uil/ambulance";
import editIcon from "@iconify-icons/uil/edit";
import timesCircle from "@iconify-icons/uil/times-circle";
import folderOpen from "@iconify-icons/uil/folder-open";

import JSONPretty from "react-json-pretty";
import NumberFormat from "react-number-format";

import { SKUS, CONTACTS, CLIENTS } from "./queries.jsx";

function ClientAboutBrief({ client }) {
  if (client.metadata && client.metadata.about) {
    return <p>{client.metadata.about}</p>;
  }
  return null;
}

function ClientDetail({ client }) {
  let details = [
    <Media>
      <ClientImage client={client} width={200} height={200}></ClientImage>
      <Media.Body style={{ marginLeft: 10 }}>
        <h4>{client.company}</h4>
        <p className="text-muted">
          <Link to={"/clients/" + client.uid}>{client.uid}</Link>
        </p>
        <ClientAboutBrief client={client}></ClientAboutBrief>
      </Media.Body>
    </Media>,
    <Row>
      <Col md={6} className="p-3">
        <ClientInvoiceList client={client}></ClientInvoiceList>
      </Col>
      <Col md={6} className="p-3">
        <ClientContactShort client={client}></ClientContactShort>
      </Col>
    </Row>,
  ];
  return details;
}

function ClientInvoiceList({ client }) {
  let data = [<h5>Invoices</h5>];
  if (client.invoices.edges.length < 1) {
    data.push(<Alert>no invoices found for client</Alert>);
  } else {
    for (invoice in client.invoices.edges) {
      data.push(invoice.id);
    }
  }
  return data;
}

function ClientContactShort({ client }) {
  if (!client.contact) {
    return [];
  }
  return [
    <Alert variant="info">
      <h5>Contact</h5>
      <p>{client.contact.primaryEmail}</p>
      <p>{client.contact.name}</p>
      <Link to={"/contacts/" + client.contact.uid}>
        <Button>View</Button>
      </Link>
    </Alert>,
  ];
}

function ClientBreadcrumbs() {
  let params = useParams();
  let crumbs = ["Clients"];
  if (params.uid) {
    crumbs.push(params.uid);
  }
  return crumbs.map((c) => <Breadcrumb.Item>{c}</Breadcrumb.Item>);
}

function Clients() {
  const { loading, error, data } = useQuery(CLIENTS, {
    variables: useParams(),
  });

  if (loading) return <GraphQLLoading></GraphQLLoading>;
  if (error) return <p>Error :(</p>;

  return [
    <Breadcrumb>
      <ClientBreadcrumbs></ClientBreadcrumbs>
    </Breadcrumb>,
    data.clients.edges.map(({ node }) => (
      <div key={node.uid}>
        <ClientDetail client={node}></ClientDetail>
      </div>
    )),
  ];
}

function ClientImage({ client, width, height }) {
  let placeholder =
    client.metadata.profile_image_url || "http://placekitten.com/200/200";
  return (
    <Image width={width} height={height} src={placeholder} thumbnail></Image>
  );
}

function Contacts() {
  const { loading, error, data } = useQuery(CONTACTS, {
    variables: useParams(),
  });

  if (loading) return <GraphQLLoading></GraphQLLoading>;
  if (error) return <p>Error :(</p>;

  return data.contacts.edges.map(({ node }) => (
    <div key={node.uid}>
      <p>
        {node.fullname}: <Link to={`/contacts/${node.uid}`}>{node.uid}</Link>
      </p>
      <JSONPretty data={node.metadata}></JSONPretty>
    </div>
  ));
}

function Metadata({ inner }) {
  let data = [];
  for (var k in inner) {
    if (inner.hasOwnProperty(k)) {
      data.push(
        <tr>
          <th>
            <pre>{k}</pre>
          </th>
          <td>
            <pre>{JSON.stringify(inner[k])}</pre>
          </td>
        </tr>
      );
    }
  }
  if (data.length < 1) {
    return [];
  }
  return [
    <Table size="sm" borderless>
      <tbody>{data}</tbody>
    </Table>,
  ];
}

function GraphQLLoading() {
  return [
    <Spinner animation="border" role="status">
      <span className="sr-only">Loading...</span>
    </Spinner>,
  ];
}

function SKURows() {
  const { loading, error, data } = useQuery(SKUS, { variables: useParams() });

  if (loading) return <GraphQLLoading></GraphQLLoading>;
  if (error) return <p>Error :(</p>;

  return data.skus.edges.map(({ node }) => <SKURow node={node}></SKURow>);
}

function Home() {
  return <div className="jumbotron">crusher.beta</div>;
}

export { Clients, Contacts, Metadata, SKUs, Home, MainNav };

function MainNav() {
  return (
    <Nav
      className="flex-column"
      variant="pills"
      activeKey={"/" + window.location.pathname.split("/")[1]}
    >
      <Nav.Item>
        <Nav.Link href="/">
          <InlineIcon icon={homeAlt}></InlineIcon> Home
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/skus">
          <InlineIcon icon={priceTagAlt}></InlineIcon> SKUs
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/contacts">
          <InlineIcon icon={userIcon}></InlineIcon> Contacts
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/clients">
          <InlineIcon icon={suitcaseIcon}></InlineIcon> Clients
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/vessels">
          <InlineIcon icon={shipIcon}></InlineIcon> Vessels
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/requests">
          <InlineIcon icon={commentAlt}></InlineIcon> Requests
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/jobs">
          <InlineIcon icon={ambulanceIcon}></InlineIcon> Jobs
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/invoices">
          <InlineIcon icon={dollarSign}></InlineIcon> Invoices
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/help">
          <InlineIcon icon={yinYang}></InlineIcon> Help
        </Nav.Link>
      </Nav.Item>
      <Nav.Item>
        <Nav.Link href="/settings">
          <InlineIcon icon={wrenchIcon}></InlineIcon> Settings
        </Nav.Link>
      </Nav.Item>
    </Nav>
  );
}

function SKUBreadcrumbs() {
  let params = useParams();
  let crumbs = ["SKUs"];
  if (params.uid) {
    crumbs.push(params.uid);
  } else if (params.tag) {
    crumbs.push("tagged");
    crumbs.push(params.tag);
  } else if (params.skuType) {
    crumbs.push(params.skuType);
  }
  return crumbs.map((c) => <Breadcrumb.Item>{c}</Breadcrumb.Item>);
}

function SKUs() {
  return [
    <Breadcrumb>
      <SKUBreadcrumbs></SKUBreadcrumbs>
    </Breadcrumb>,
    <Table borderless className="rounded" style={{ overflow: "hidden" }}>
      <thead className="bg-primary text-white">
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Price</th>
          <th>Quantity</th>
          <th>per</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <SKURows></SKURows>
      </tbody>
      <tfoot></tfoot>
    </Table>,
  ];
}

function SKUThumb({ metadata, width, height }) {
  width = width || 64;
  height = height || 64;
  if (metadata && metadata.images && metadata.images.length > 0) {
    return (
      <Image src={metadata.images[0]} width={width} height={height}></Image>
    );
  }
  return <Icon width={width} height={height} icon={userIcon}></Icon>;
}

function SKURow({ node }) {
  return [
    <tr
      key={node.uid}
      className="m-3 bg-dark text-white"
      style={{ borderRadius: 10 }}
    >
      <td className="bg-light text-dark">
        {node.name || node.metadata.name || "???"}
      </td>
      <td className="bg-light text-dark">
        <Link to={"/skus/by-type/" + node.metadata.type}>
          {node.metadata.type}
        </Link>
      </td>
      <td>
        <NumberFormat
          value={node.defaultPrice}
          decimalScale={2}
          fixedDecimalScale={true}
          displayType={"text"}
          prefix={"$"}
        ></NumberFormat>
      </td>
      <td>{node.defaultQuantity}</td>
      <td>{node.units}</td>
      <td align="center">
        <ButtonGroup>
          <Link to={`/skus/${node.uid}`}>
            <Button variant="info">
              <Icon icon={folderOpen}></Icon>
            </Button>
          </Link>
          <Button variant="warning">
            <Icon icon={editIcon}></Icon>
          </Button>
          <Button variant="danger">
            <Icon icon={timesCircle}></Icon>
          </Button>
        </ButtonGroup>
      </td>
    </tr>,
    <tr key={"extra-" + node.uid} className="alert alert-light">
      <td>
        <SKUThumb metadata={node.metadata}></SKUThumb>
      </td>
      <td>
        <JSONPretty data={node.metadata}></JSONPretty>
      </td>
      <td colSpan="4" align="right">
        <Link to={`/skus/${node.uid}`}>{node.uid}</Link>
      </td>
    </tr>,
  ];
}
