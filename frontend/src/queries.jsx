import { gql } from 'apollo-boost';

const CLIENTS = gql`
query ($id: UUID, $company: String, $companyLike: String) {
  clients(id: $id, company: $company, company_Icontains: $companyLike) {
    edges {
      node {
        clientId,
        company,
        metadata,
        contact {
          id,
          name,
          primaryEmail
        }
      }
    }
  }
}
`

const CONTACTS = gql`
query ($id: UUID, $firstNameLike: String, $lastNameLike: String, $emailLike: String) {
    contacts(id: $id, firstName_Icontains: $firstNameLike, lastName_Icontains: $lastNameLike, primaryEmail_Icontains: $emailLike) {
        edges {
            node{
                contactId,
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
    skus(id: $id, name: $nameLike, defaultPrice: $defaultPriceExact, tag: $tag, skuType: $skuType) {
        edges {
            node {
                name,
                skuId,
                metadata,
                defaultPrice,
                defaultQuantity
            }
        }
    }
}`;

export {CLIENTS, CONTACTS, SKUS}
