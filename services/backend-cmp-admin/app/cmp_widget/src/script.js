import { translations } from "./translations.js";
import styles from "./styles.css?raw";
import template from "./template.html?raw";

// 3. CORE WIDGET LOGIC
import { initWidget } from "./cmp.js";
const websiteId = "{self.widget_name}";
// Execute the widget initialization with all loaded assets
initWidget({ translations, template, styles, websiteId });
