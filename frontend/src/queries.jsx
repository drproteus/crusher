import { gql } from "apollo-boost";

const CLIENTS = gql`
  query($uid: UUID, $company: String, $companyLike: String) {
    clients(uid: $uid, company: $company, company_Icontains: $companyLike) {
      edges {
        node {
          uid
          company
          metadata
          contact {
            uid
            name
            primaryEmail
          }
          invoices {
            edges {
              node {
                uid
                paidBalance
                initialBalance
                lineItems {
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

export { CLIENTS, CONTACTS, SKUS };
