import React from 'react';

const ImportantContactsPage: React.FC = () => {
  const contacts = [
    { name: 'Dr. Jane Doe', phone: '555-123-4567' },
    { name: 'Dr. John Smith', phone: '555-345-6789' },
];

return (
  <div>
    <h1>Important Contacts</h1>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Phone</th>
        </tr>
      </thead>
      <tbody>
        {contacts.map((contact, index) => (
          <tr key={index}>
            <td>{contact.name}</td>
            <td>{contact.phone}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
};

export default ImportantContactsPage;
