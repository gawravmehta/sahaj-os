import React from "react";

const CookiePolicyPage = () => {
  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Cookie Policy</h1>

      <p style={styles.paragraph}>
        Welcome to [Your Bank Name] (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;). This Cookie Policy explains how we use cookies and similar technologies when you visit our website{" "}
        <a href="[Your Website URL]" style={styles.link}>[Your Website URL]</a>{" "}
        (the &quot;Website&quot;). It also explains what these technologies are and why we use them, as well as your rights to control our use of them.
      </p>

      <h2 style={styles.subHeading}>What are Cookies?</h2>
      <p style={styles.paragraph}>
        Cookies are small data files that are placed on your computer or mobile device when you visit a website. Cookies are widely used by website owners in order to make their websites work, or to work more efficiently, as well as to provide reporting information.
      </p>
      <p style={styles.paragraph}>
        Cookies set by the website owner (in this case, [Your Bank Name]) are called &quot;first-party cookies.&quot; Cookies set by parties other than the website owner are called &quot;third-party cookies.&quot; Third-party cookies enable third-party features or functionality to be provided on or through the website (e.g., advertising, interactive content, and analytics). The parties that set these third-party cookies can recognize your computer both when it visits the website in question and when it visits certain other websites.
      </p>

      <h2 style={styles.subHeading}>Why Do We Use Cookies?</h2>
      <p style={styles.paragraph}>
        We use first-party and third-party cookies for several reasons. Some cookies are required for our Website to operate, and we refer to these as &quot;essential&quot; or &quot;strictly necessary&quot; cookies. Other cookies also enable us to track and target the interests of our users to enhance the experience on our Website. Third parties serve cookies through our Website for advertising, analytics, and other purposes. This is described in more detail below.
      </p>

      <h2 style={styles.subHeading}>Types of Cookies We Use:</h2>
      <ul style={styles.list}>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Essential Cookies:</strong> These cookies are strictly necessary to provide you with services available through our Website and to use some of its features, such as access to secure areas. Without these cookies, services you have asked for, like transactional banking, cannot be provided.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Performance and Functionality Cookies:</strong> These cookies are used to enhance the performance and functionality of our Website but are non-essential to their use. However, without these cookies, certain functionality (like remembering your preferences) may become unavailable.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Analytics and Customization Cookies:</strong> These cookies collect information that is used either in aggregate form to help us understand how our Website is being used or how effective our marketing campaigns are, or to help us customize our Website for you.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Advertising Cookies:</strong> These cookies are used to make advertising messages more relevant to you. They perform functions like preventing the same ad from continuously reappearing, ensuring that ads are properly displayed for advertisers, and in some cases selecting advertisements that are based on your interests.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Social Networking Cookies:</strong> These cookies are used to enable you to share pages and content that you find interesting on our Website through third-party social networking and other websites. These cookies may also be used for advertising purposes.
        </li>
      </ul>

      <h2 style={styles.subHeading}>How Can You Control Cookies?</h2>
      <p style={styles.paragraph}>
        You have the right to decide whether to accept or reject cookies. You can exercise your cookie preferences by clicking on the appropriate opt-out links provided in the cookie consent banner or by setting your browser controls.
      </p>
      <ul style={styles.list}>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Browser Controls:</strong> You can set or amend your web browser controls to accept or refuse cookies. If you choose to reject cookies, you may still use our Website, though your access to some functionality and areas of our Website may be restricted. As the means by which you can refuse cookies through your web browser controls vary from browser to browser, you should visit your browser&apos;s help menu for more information.
        </li>
        <li style={styles.listItem}>
          <strong style={styles.strong}>Third-Party Opt-Outs:</strong> Many advertising networks offer you a way to opt-out of targeted advertising. You can find out more by visiting:
          <ul style={styles.nestedList}>
            <li style={styles.nestedListItem}><a href="http://www.aboutads.info/choices/" target="_blank" rel="noopener noreferrer" style={styles.link}>Digital Advertising Alliance</a></li>
            <li style={styles.nestedListItem}><a href="http://www.youronlinechoices.com/" target="_blank" rel="noopener noreferrer" style={styles.link}>YourOnlineChoices</a></li>
          </ul>
        </li>
      </ul>

      <h2 style={styles.subHeading}>Do Not Track</h2>
      <p style={styles.paragraph}>
        Some Internet browsers may transmit &quot;Do Not Track&quot; signals. As there is no standard for how to respond to &quot;Do Not Track&quot; signals, we do not currently respond to them.
      </p>

      <h2 style={styles.subHeading}>Updates to this Cookie Policy</h2>
      <p style={styles.paragraph}>
        We may update this Cookie Policy from time to time in order to reflect, for example, changes to the cookies we use or for other operational, legal, or regulatory reasons. Please therefore re-visit this Cookie Policy regularly to stay informed about our use of cookies and related technologies.
      </p>
      <p style={styles.paragraph}>
        The date at the bottom of this Cookie Policy indicates when it was last updated.
      </p>

      <h2 style={styles.subHeading}>Where Can You Get Further Information?</h2>
      <p style={styles.paragraph}>
        If you have any questions about our use of cookies or other technologies, please email us at <a href="mailto:[Your Support Email]" style={styles.link}>[Your Support Email]</a> or contact us at:
      </p>
      <p style={styles.paragraph}>
        [Your Bank Name]<br />
        [Your Bank Address]<br />
        [Your Bank Phone Number]
      </p>

      <p style={styles.updateDate} >Last updated: June 17, 2025</p>
    </div>
  );
};

// Basic inline styles for a clean, readable layout, inspired by corporate banking sites
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
  nestedList: {
    marginLeft: '20px',
    marginTop: '5px',
  },
  nestedListItem: {
    marginBottom: '5px',
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


export default CookiePolicyPage;