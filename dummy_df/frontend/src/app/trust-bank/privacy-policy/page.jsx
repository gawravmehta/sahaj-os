import React from "react";

const PrivacyPolicyPage = () => {
  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Privacy Policy</h1>

      <p style={styles.paragraph}>
        At [Your Bank Name] (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;), we are committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and protect your personal information when you use our services, visit our website{" "}
        <a href="[Your Website URL]" style={styles.link}>[Your Website URL]</a>, or interact with us.
      </p>
      <p style={styles.paragraph}>
        By accessing or using our services, you agree to the terms of this Privacy Policy. If you do not agree with the practices described in this policy, please do not use our services.
      </p>

      <h2 style={styles.subHeading}>1. Information We Collect</h2>
      <p style={styles.paragraph}>
        We collect various types of information to provide and improve our services, including:
      </p>
      <ul style={styles.list}>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Personal Identifiable Information (PII):</strong> This includes information that can be used to identify you directly or indirectly, such as your name, address, email address, phone number, date of birth, Aadhaar number, PAN number, financial details (e.g., account numbers, transaction history), and government-issued identification.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Financial Information:</strong> Details related to your bank accounts, credit cards, investments, loan applications, and transaction history.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Demographic Information:</strong> Information such as your age, gender, occupation, and income level.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Technical and Usage Data:</strong> Information about your device (IP address, device type, operating system), browser type, pages viewed, time spent on our website/app, links clicked, and other diagnostic data. This is often collected via cookies and similar technologies (please refer to our <a href="/cookie-policy" style={styles.link}>Cookie Policy</a> for more details).
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Location Information:</strong> If you grant permission, we may collect your precise or approximate location information.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Communication Data:</strong> Information you provide when you communicate with us, such as customer service inquiries, feedback, or survey responses.
        </li>
      </ul>

      <h2 style={styles.subHeading}>2. How We Collect Information</h2>
      <p style={styles.paragraph}>We collect information from various sources, including:</p>
      <ul style={styles.list}>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Directly from You:</strong> When you open an account, apply for a product, fill out forms, participate in surveys, communicate with customer service, or register for our online services.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>From Third Parties:</strong> We may receive information from credit bureaus, government agencies, fraud prevention agencies, and other third-party service providers, where permitted by law.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Automatically:</strong> Through cookies, web beacons, and similar technologies when you visit our website or use our mobile applications.
        </li>
      </ul>

      <h2 style={styles.subHeading}>3. How We Use Your Information</h2>
      <p style={styles.paragraph}>We use the information we collect for various purposes, including:</p>
      <ul style={styles.list}>
        <li style={styles.listItem}>
          <strong style={styles.strong}>To Provide and Manage Services:</strong> To process transactions, manage your accounts, provide customer support, and deliver the products and services you request.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>To Improve and Personalize Services:</strong> To understand how you use our services, enhance user experience, develop new features, and tailor content and offers.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>For Marketing and Communication:</strong> To send you updates, promotional materials, and information about products and services that may interest you. You can opt-out of marketing communications at any time.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>For Security and Fraud Prevention:</strong> To protect against fraud, unauthorized transactions, claims, and other liabilities, and to manage risk exposure.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>For Compliance and Legal Obligations:</strong> To comply with applicable laws, regulations, legal processes, and governmental requests.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>For Analytics and Research:</strong> To perform data analysis, research, and for statistical purposes.
        </li>
      </ul>

      <h2 style={styles.subHeading}>4. Disclosure of Your Information</h2>
      <p style={styles.paragraph}>
        We may share your personal information with third parties in the following circumstances:
      </p>
      <ul style={styles.list}>
        <li style={styles.listItem}>
          <strong style={styles.strong}>With Your Consent:</strong> We may share information with third parties when we have your explicit consent to do so.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Service Providers:</strong> With third-party vendors, consultants, and other service providers who perform services on our behalf, such as payment processing, data analysis, IT services, marketing, and customer support. These parties are contractually obligated to protect your information and use it only for the purposes for which it was disclosed.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Affiliates and Group Companies:</strong> With our subsidiaries, affiliates, and other entities within the [Your Bank Name] group for business operations, compliance, and service delivery.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Legal Requirements:</strong> When required by law, regulation, court order, or governmental request, or to protect our rights, property, or safety, or the rights, property, or safety of others.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Business Transfers:</strong> In connection with, or during negotiations of, any merger, sale of company assets, financing, or acquisition of all or a portion of our business by another company.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Credit Bureaus and Fraud Prevention Agencies:</strong> To assess creditworthiness, prevent fraud, and comply with reporting obligations.
        </li>
      </ul>

      <h2 style={styles.subHeading}>5. Data Security</h2>
      <p style={styles.paragraph}>
        We implement robust administrative, technical, and physical security measures designed to protect your personal information from unauthorized access, use, disclosure, alteration, or destruction. These measures include encryption, firewalls, secure server facilities, and access controls. However, no method of transmission over the Internet or electronic storage is 100% secure. Therefore, while we strive to use commercially acceptable means to protect your personal information, we cannot guarantee its absolute security.
      </p>

      <h2 style={styles.subHeading}>6. Your Rights</h2>
      <p style={styles.paragraph}>
        Depending on applicable laws, you may have certain rights regarding your personal information, including the right to:
      </p>
      <ul style={styles.list}>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Access:</strong> Request access to the personal information we hold about you.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Correction:</strong> Request correction of inaccurate or incomplete personal information.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Withdraw Consent:</strong> Withdraw your consent for certain processing activities, where applicable.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Opt-Out of Marketing:</strong> Opt-out of receiving marketing communications from us.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Deletion/Erasure:</strong> Request the deletion of your personal information, subject to legal and regulatory retention requirements.
        </li>
      </ul>
      <p style={styles.paragraph}>
        To exercise any of these rights, please contact us using the details provided in the &quot;Contact Us&quot; section below.
      </p>

      <h2 style={styles.subHeading}>7. Data Retention</h2>
      <p style={styles.paragraph}>
        We retain your personal information for as long as necessary to fulfill the purposes for which it was collected, including for the purposes of satisfying any legal, accounting, or reporting requirements.
      </p>

      <h2 style={styles.subHeading}>8. Links to Third-Party Websites</h2>
      <p style={styles.paragraph}>
        Our website may contain links to third-party websites or services that are not operated by us. We are not responsible for the privacy practices or the content of these third-party sites. We encourage you to review the privacy policies of any third-party sites you visit.
      </p>

      <h2 style={styles.subHeading}>9. Children&apos;s Privacy</h2>
      <p style={styles.paragraph}>
        Our services are not intended for individuals under the age of 18. We do not knowingly collect personal information from children without parental consent. If we become aware that we have collected personal information from a child without verifiable parental consent, we will take steps to remove that information from our servers.
      </p>

      <h2 style={styles.subHeading}>10. Changes to This Privacy Policy</h2>
      <p style={styles.paragraph}>
        We may update this Privacy Policy from time to time to reflect changes in our practices, technology, legal requirements, and other factors. We will notify you of any material changes by posting the new Privacy Policy on this page and updating the &quot;Last updated&quot; date. We encourage you to review this Privacy Policy periodically.
      </p>

      <h2 style={styles.subHeading}>11. Contact Us</h2>
      <p style={styles.paragraph}>
        If you have any questions or concerns about this Privacy Policy or our privacy practices, please contact us at:
      </p>
      <p style={styles.paragraph}>
        [Your Bank Name]<br />
        [Your Bank Address]<br />
        Email: <a href="mailto:[Your Support Email]" style={styles.link}>[Your Support Email]</a><br />
        Phone: [Your Bank Phone Number]
      </p>

      <p style={styles.updateDate}>Last updated: June 17, 2025</p>
    </div>
  );
};

// Reusing the same basic styles for consistency
const styles = {
  container: {
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    lineHeight: '1.6',
    color: '#333',
    maxWidth: '900px',
    margin: '40px auto',
    padding: '20px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
    borderRadius: '8px',
    backgroundColor: '#fff',
  },
  heading: {
    color: '#0047AB', // A professional blue
    fontSize: '2.5em',
    marginBottom: '20px',
    borderBottom: '2px solid #eee',
    paddingBottom: '10px',
    textAlign: 'center',
  },
  subHeading: {
    color: '#0047AB',
    fontSize: '1.8em',
    marginTop: '30px',
    marginBottom: '15px',
  },
  paragraph: {
    marginBottom: '15px',
    fontSize: '1em',
  },
  list: {
    marginLeft: '20px',
    marginBottom: '15px',
  },
  listItem: {
    marginBottom: '10px',
    fontSize: '1em',
  },
  strong: {
    fontWeight: 'bold',
  },
  link: {
    color: '#007BFF', // A standard link blue
    textDecoration: 'none',
  },
  updateDate: {
    marginTop: '40px',
    fontSize: '0.9em',
    color: '#777',
    textAlign: 'right',
  }
};

export default PrivacyPolicyPage;