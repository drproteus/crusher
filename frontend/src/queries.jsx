import { gql } from 'apollo-boost';

const CLIENTS = gql`
query ($id: UUID, $company: String, $companyLike: String) {
  clients(uid: $id, company: $company, company_Icontains: $companyLike) {
    edges {
      node {
        uid,
        company,
        metadata,
        contact {
          uid,
          name,
          primaryEmail
        },
        invoices {
          edges {
            node {
              uid,
              paidBalance,
              initialBalance,
              lineItems {
                uid,
                subtotal
              }
            }
          }
        }
      }
    }
  }
}
`

const CONTACTS = gql`
query ($id: UUID, $firstNameLike: String, $lastNameLike: String, $emailLike: String) {
    contacts(uid: $id, firstName_Icontains: $firstNameLike, lastName_Icontains: $lastNameLike, primaryEmail_Icontains: $emailLike) {
        edges {
            node{
                uid,
                primaryEmail,
                phoneNumber,
                name,
                fullname,
                title,
                firstName,
                lastName,
                mailingAddress,
                billingAddress
            }
        }
    }
}
`;

const SKUS = gql`
query ($id: UUID, $nameLike: String, $defaultPriceExact: Float, $tag: String, $skuType: String) {
    skus(uid: $id, name: $nameLike, defaultPrice: $defaultPriceExact, tag: $tag, skuType: $skuType) {
        edges {
            node {
                name,
                uid,
                units,
                metadata,
                defaultPrice,
                defaultQuantity
            }
        }
    }
}`;

export {CLIENTS, CONTACTS, SKUS}
