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
import ListGroup from "react-bootstrap/ListGroup";
import Badge from "react-bootstrap/Badge";

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
import plusIcon from "@iconify-icons/uil/plus";
import searchIcon from "@iconify-icons/uil/search";

import JSONPretty from "react-json-pretty";
import NumberFormat from "react-number-format";

import { SKUS, CONTACTS, CLIENTS } from "./queries.jsx";
import { CREATE_CLIENT, UPDATE_CLIENT, UPDATE_METADATA } from "./mutations.jsx"

function ClientBreadcrumbs() {
  let params = useParams();
  let crumbs = ["Clients"];
  if (params.uid) {
    crumbs.push(params.uid);
  }
  return crumbs.map((c) => <Breadcrumb.Item>{c}</Breadcrumb.Item>);
}

function ClientsAsList() {
  const { loading, error, data } = useQuery(CLIENTS, {
    variables: useParams(),
  });

  if (loading) return <GraphQLLoading></GraphQLLoading>;
  if (error) return <p>Error :(</p>;
  return data.clients.edges.map(({ node }) => (
    <ListGroup.Item className="bg-light">
      <ClientImage client={node} width={32} height={32}>
        {" "}
      </ClientImage>
      <Link to={"/clients/" + node.uid} className="m-3">
        {node.company}
      </Link>
      <div className="float-right">
        <span className="text-muted">invoices: </span>
        <Badge className="m-1" variant="secondary">
          {node.invoiceCounts.drafts} drafts
        </Badge>
        <Badge className="m-1" variant="primary">
          {node.invoiceCounts.open} open
        </Badge>
        <Badge className="m-1" variant="warning">
          {node.invoiceCounts.paid_partial} paid partial
        </Badge>
        <Badge className="m-1" variant="success">
          {node.invoiceCounts.paid_partial} paid full
        </Badge>
        <Badge className="m-1" variant="dark">
          {node.invoiceCounts.void} void
        </Badge>
        <Badge className="m-1" variant="danger">
          {node.invoiceCounts.closed} closed
        </Badge>
      </div>
    </ListGroup.Item>
  ));
}

function Clients() {
  return [
    <Row>
      <Col md={8}>
        <Breadcrumb>
          <ClientBreadcrumbs></ClientBreadcrumbs>
        </Breadcrumb>
      </Col>
      <Col>
        <div className="text-right m-1">
          <ButtonGroup>
            <Button variant="info">
              <InlineIcon icon={searchIcon}></InlineIcon> Find Client
            </Button>
            <Button>
              <InlineIcon icon={plusIcon}></InlineIcon> Add Client
            </Button>
          </ButtonGroup>
        </div>
      </Col>
    </Row>,
    <ListGroup variant="flush">
      <ClientsAsList></ClientsAsList>
    </ListGroup>,
  ];
}

function ClientImage({ client, width, height }) {
  let placeholder = client.imageUrl || "http://placekitten.com/200/200";
  return (
    <Image
      width={width}
      height={height}
      src={placeholder}
      roundedCircle
    ></Image>
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

export { Clients, Contacts, SKUs, Home, MainNav };

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
        <Nav.Link href="/tasks">
          <InlineIcon icon={commentAlt}></InlineIcon> Tasks
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

function SKUThumb({ url, width, height }) {
  width = width || 64;
  height = height || 64;
  if (url && url.length > 0) {
    return <Image src={url} width={width} height={height}></Image>;
  }
  return <Icon width={width} height={height} icon={userIcon}></Icon>;
}

function SKURow({ node }) {
  return [
    <tr
      key={node.uid}
      className="m-3 bg-light text-dark"
      style={{ borderRadius: 10 }}
    >
      <td>{node.name || node.metadata.name || "???"}</td>
      <td>
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
    <tr key={"extra-" + node.uid}>
      <td>
        <SKUThumb url={node.imageUrl}></SKUThumb>
      </td>
      <td>
        <JSONPretty data={node.metadata}></JSONPretty>
      </td>
      <td colSpan="4" align="right">
        <Link to={`/skus/${node.uid}`} className="text-muted">
          {node.uid}
        </Link>
      </td>
    </tr>,
  ];
}
