import { gql } from "apollo-boost";

const CREATE_CLIENT = gql`
  mutation CreateClient(
    $company: String!
    $contactUid: UUID
    $metadata: GenericScalar
  ) {
    modifyClient(
      data: { company: $company, contactUid: $contactUid, metadata: $metadata }
    ) {
      client {
        uid
        company
        contact {
          name
          primaryEmail
        }
        metadata
      }
    }
  }
`;

const UPDATE_CLIENT = gql`
  mutation UpdateClient(
    $uid: UUID!
    $company: String
    $contactUid: UUID
    $metadata: GenericScalar
  ) {
    modifyClient(
      uid: $uid
      data: { company: $company, contactUid: $contactUid, metadata: $metadata }
    ) {
      client {
        uid
        company
        contact {
          name
          primaryEmail
        }
        metadata
      }
    }
  }
`;

const DELETE_CLIENT = gql`
  mutation DeleteClient($uid: UUID!) {
    deleteClient(uid: $uid) {
      ok
    }
  }
`;

const UPDATE_METADATA = gql`
  mutation UpdateMetadata(
    $uid: UUID!
    $metadata: GenericScalar!
    $mode: String
  ) {
    modifyMetadata(uid: $uid, metadata: $metadata, mode: $mode) {
      metadata
      uid
      mode
      parentType
    }
  }
`;

export { CREATE_CLIENT, UPDATE_CLIENT, UPDATE_METADATA, DELETE_CLIENT };
