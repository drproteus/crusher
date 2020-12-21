import React from "react";
import { CREATE_CLIENT, UPDATE_CLIENT, UPDATE_METADATA } from "./mutations.jsx";
import { Formik, Field, Form } from "formik";
import { useMutation } from "@apollo/react-hooks";
import { Redirect } from "react-router-dom";
import Spinner from "react-bootstrap/Spinner";
import JSONPretty from "react-json-pretty";

function CreateClient() {
  const [createClient] = useMutation(CREATE_CLIENT, {
    onCompleted: () => window.location.replace("/clients"), // hacky redirect..
  });

  return [
    <Formik
      initialValues={{
        metadata: "{}",
      }}
      onSubmit={(values) => {
        if (values.metadata !== undefined) {
          values.metadata = JSON.parse(values.metadata);
        }
        createClient({ variables: values });
      }}
    >
      <Form className="p-3">
        <h3>New Client</h3>
        <div className="form-group">
          <label htmlFor="company"></label>
          <Field
            className="form-control"
            id="company"
            name="company"
            placeholder="Starfleet"
          ></Field>
        </div>
        <div className="form-group">
          <label htmlFor="metadata"></label>
          <Field
            className="form-control"
            as="textarea"
            name="metadata"
            id="metadata"
            type="text"
          ></Field>
        </div>
        <button className="btn btn-primary" type="submit">
          Create Client
        </button>
      </Form>
    </Formik>,
  ];
}

export { CreateClient };
