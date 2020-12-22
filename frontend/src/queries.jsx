import { gql } from "apollo-boost";

const CLIENTS = gql`
  query($uid: UUID, $company: String, $companyLike: String) {
    clients(uid: $uid, company: $company, company_Icontains: $companyLike) {
      edges {
        node {
          uid
          createdAt
          updatedAt
          company
          metadata
          imageUrl
          invoiceCounts
        }
      }
    }
  }
`;

const CLIENT_DETAIL = gql`
  query($uid: UUID!, $invoiceState: String) {
    client(uid: $uid) {
      uid
      createdAt
      updatedAt
      company
      metadata
      imageUrl
      invoiceCounts
      contact {
        uid
        name
        primaryEmail
      }
      attachments {
        edges {
          node {
            uid
            url
            name
            createdAt
          }
        }
      }
      forms {
        edges {
          node {
            uid
            url
            templateFile
            createdAt
          }
        }
      }
      invoices(state: $invoiceState) {
        edges {
          node {
            uid
            paidBalance
            initialBalance
            attachments {
              edges {
                node {
                  uid
                  url
                  name
                  createdAt
                }
              }
            }
            lineItems {
              edges {
                node {
                  uid
                  subtotal
                }
              }
            }
          }
        }
      }
    }
  }
`;

const CONTACTS = gql`
  query(
    $uid: UUID
    $firstNameLike: String
    $lastNameLike: String
    $emailLike: String
  ) {
    contacts(
      uid: $uid
      firstName_Icontains: $firstNameLike
      lastName_Icontains: $lastNameLike
      primaryEmail_Icontains: $emailLike
    ) {
      edges {
        node {
          uid
          primaryEmail
          phoneNumber
          name
          fullname
          title
          firstName
          lastName
          mailingAddress
          billingAddress
          imageUrl
        }
      }
    }
  }
`;

const SKUS = gql`
  query(
    $uid: UUID
    $nameLike: String
    $defaultPriceExact: Float
    $tag: String
    $skuType: String
  ) {
    skus(
      uid: $uid
      name: $nameLike
      defaultPrice: $defaultPriceExact
      tag: $tag
      skuType: $skuType
    ) {
      edges {
        node {
          name
          uid
          units
          metadata
          defaultPrice
          defaultQuantity
          imageUrl
        }
      }
    }
  }
`;

export { CLIENT_DETAIL, CLIENTS, CONTACTS, SKUS };
