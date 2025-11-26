// import { translations } from "./translations.js";
// import styles from "./styles.css?raw";
// import template from "./template.html?raw";
/**
 * Main widget initialization function.
 * @param {Object} assets - Object containing dynamic and static assets.
 * @param {Object} assets.translations - The complete translations JSON.
 * @param {string} assets.template - The generated HTML string.
 * @param {string} assets.styles - The static CSS string.
 * @param {string} assets.websiteId - The ID of the website.
 * @param {string} assets.consentApiBaseUrl - The base URL for the consent API.
 */
export function initWidget({ translations, template, styles, websiteId, consentApiBaseUrl }) {
  console.log("CMP script loaded ✅");
  // --- Root + Shadow DOM ---
  const cmpRoot = document.createElement("div");
  document.body.appendChild(cmpRoot);
  const shadowRoot = cmpRoot.attachShadow({ mode: "open" });

  // Inject CSS
  const styleTag = document.createElement("style");
  styleTag.textContent = styles;
  shadowRoot.appendChild(styleTag);

  // Inject HTML
  const container = document.createElement("div");
  container.innerHTML = template;
  shadowRoot.appendChild(container);

  // --- Utilities ---
  function $(selector) {
    return shadowRoot.querySelector(selector);
  }
  function $$(selector) {
    return shadowRoot.querySelectorAll(selector);
  }

  // --- Consent State ---
  function initConsentState() {
    const saved = localStorage.getItem("consentState");
    const categories = Object.keys(translations.eng.categories);
    let state = {};

    categories.forEach((cat) => {
      state[cat] = cat === "essential"; // essential always true
    });

    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        state = { ...state, ...parsed };
      } catch (e) {
        console.error("Failed to parse saved consentState", e);
      }
    }

    localStorage.setItem("consentState", JSON.stringify(state));
    return state;
  }

  let consentState = initConsentState();

  function saveConsentState() {
    localStorage.setItem("consentState", JSON.stringify(consentState));
  }

  // --- Helper Functions ---
  function renderCategoryDetails(lang, category) {
    const data = translations[lang].categories[category];
    if (!data) return;

    let cookieDetailsHtml = "";
    if (data.cookies && data.cookies.length > 0) {
      data.cookies.forEach((cookie) => {
        cookieDetailsHtml += `
          <div class="cookie-details">
            <div class="cookie-header" data-toggle="true">
              <div class="cookie-name">${cookie.name}</div>
              <div class="expand-icon"></div>
            </div>
            <div class="cookie-info">
              <div style="margin-bottom: 8px; font-size: 12px; color: #212121;">${cookie.description}</div>
              <div class="cookie-meta"><span>${cookie.domain}</span><span>${cookie.expiry}</span></div>
            </div>
          </div>`;
      });
    } else {
      cookieDetailsHtml = `<p style="font-size: 13px; color: #878787;">No specific cookies listed for this category.</p>`;
    }

    $("#category-details").innerHTML = `
      <div class="category-content" data-content="${category}">
        <div class="category-header">
          <div class="category-name">${data.name}</div>
          <div class="toggle-switch ${
            category === "essential" ? "active disabled" : ""
          }" data-toggle-switch="true"></div>
        </div>
        <div class="category-description">${data.description}</div>
        ${cookieDetailsHtml}
      </div>`;

    syncTogglesWithConsent();
  }

  function setLanguage(lang) {
    localStorage.setItem("selectedLanguage", lang);
    const langData = translations[lang];

    const languageNames = {
      eng: "English",
      hin: "हिन्दी",
      ben: "বাংলা",
      tel: "తెలుగు",
      mar: "मराठी",
      tam: "தமிழ்",
      urd: "اردو",
      guj: "ગુજરાતી",
      kan: "ಕನ್ನಡ",
      mal: "മലയാളം",
      ori: "ଓଡ଼ିଆ",
      pan: "ਪੰਜਾਬੀ",
      asm: "অসমীয়া",
      mai: "मैथिली",
      sat: "ᱥᱟᱱᱛᱟᱲᱤ",
      kas: "كٲشُر",
      nep: "नेपाली",
      snd: "سنڌي",
      kok: "कोंकणी",
      doi: "डोगरी",
      mni: "মেইতেইলোন্",
      brx: "बोड़ो",
      san: "संस्कृत",
    };

    const createLinkedText = (text, links) => {
      let html = text;
      links.forEach((link) => {
        const regex = new RegExp(`(${link.text})`, "g");
        html = html.replace(
          regex,
          `<a href="${link.url}" target="_blank" class="cookie-policy-link">$1</a>`
        );
      });
      return html;
    };

    const langText = languageNames[lang] || lang;

    $("#selected-language-banner").textContent = langText;
    $("#selected-language-modal").textContent = langText;

    $("#open-preferences-btn").textContent = langData.bannerButtons.settings;
    $("#cookie-settings-btn").textContent = langData.bannerButtons.settings;
    $("#accept-essential-btn").textContent = langData.bannerButtons.essential;
    $("#accept-all-btn").textContent = langData.bannerButtons.acceptAll;

    $("#cookie-content").innerHTML = createLinkedText(
      langData.description,
      langData.links
    );

    $("#preference-title").textContent = langData.modalTitle;
    $("#preference-description").innerHTML = createLinkedText(
      langData.description,
      langData.links
    );
    $("#consent-section-title").textContent = langData.modalSectionTitle;

    $(".btn-reject").textContent = langData.modalButtons.rejectAll;
    $(".btn-allow").textContent = langData.modalButtons.allowAll;
    $(".btn-confirm").textContent = langData.modalButtons.confirm;

    $("#powered-by-text").textContent = langData.poweredBy;

    $$(".category-item").forEach((item) => {
      const categoryKey = item.dataset.category;
      item.textContent = langData.categories[categoryKey].name;
    });

    const activeCategory =
      $(".category-item.active")?.dataset.category || "essential";
    renderCategoryDetails(lang, activeCategory);
  }

  function toggleSwitch(element) {
    if (element.classList.contains("disabled")) return;
    element.classList.toggle("active");

    const parent = element.closest(".category-content");
    if (!parent) return;
    const category = parent.dataset.content;

    consentState[category] = element.classList.contains("active");
    saveConsentState();
  }

  function toggleCookieInfo(element) {
    const cookieInfo = element.nextElementSibling;
    const expandIcon = element.querySelector(".expand-icon");
    cookieInfo.classList.toggle("expanded");
    expandIcon.classList.toggle("expanded");
  }

  function hideBanner() {
    $("#cookie-banner").classList.remove("show");
    setTimeout(() => {
      $("#cookie-banner").style.display = "none";
      $("#open-preferences-btn").style.display = "block";
    }, 400);
  }

  function showBanner() {
    $("#cookie-banner").style.display = "block";
    setTimeout(() => $("#cookie-banner").classList.add("show"), 10);
    $("#open-preferences-btn").style.display = "none";
  }

  function closePreferenceModal() {
    $("#preference-modal").classList.remove("show");
    if (localStorage.getItem("cookieConsent")) {
      $("#open-preferences-btn").style.display = "block";
    }
  }

  /**
   * IMPORTANT: This function now correctly finds scripts with the "text/plain" type
   * and dynamically executes them based on the consented categories.
   */
  function executeScripts() {
    document
      .querySelectorAll('script[data-cmp-injected="true"]')
      .forEach((script) => {
        if (script.parentNode) {
          script.parentNode.removeChild(script);
        }
      });
    const consentedCategories = Object.keys(consentState).filter(
      (cat) => consentState[cat]
    );

    const allScripts = document.querySelectorAll(
      'script[data-cookie-category][type="text/plain"]'
    );

    // Iterate through all scripts and execute only those with a consented category.
    allScripts.forEach((script) => {
      const category = script.dataset.cookieCategory;
      if (consentedCategories.includes(category)) {
        // Create a new script element to execute the content
        const newScript = document.createElement("script");
        newScript.setAttribute("async", "async");
        newScript.setAttribute("data-cmp-injected", "true");
        // If the script has a data-src, set the src attribute
        if (script.dataset.src) {
          newScript.src = script.dataset.src;
          newScript.onload = () =>
            console.log(`Script from ${newScript.src} loaded and executed.`);
        }
        // Otherwise, copy the inline content
        else {
          newScript.textContent = script.textContent;
        }

        // Append the new script to the body, which causes it to execute
        document.body.appendChild(newScript);
      }
    });
  }

  function syncTogglesWithConsent() {
    $$(".toggle-switch:not(.disabled)").forEach((toggle) => {
      const parent = toggle.closest(".category-content");
      if (!parent) return;
      const category = parent.dataset.content;
      toggle.classList.toggle("active", consentState[category]);
    });
  }

  // --- NEW LOGIC: Use 'en' as the source of truth for cookie names ---

  async function sendConsentToApi(websiteId) {
    if (!consentState || Object.keys(consentState).length === 0) {
      console.error(
        "Consent state is empty or undefined. Cannot send payload."
      );
      return;
    }

    const payload = {
      category_choices: consentState,
      user_id: window.cmpUserId || null,
      website_id: websiteId,
      language: localStorage.getItem("selectedLanguage") || "eng",
    };

    const API_ENDPOINT = `${consentApiBaseUrl}/v1/consent`;

    try {
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 429) {
        console.warn(
          "API Rate Limit Exceeded. Consent not sent. Retry after some time."
        );
        // Optional: save consent locally to retry later
        return;
      }

      if (response.ok) {
        console.log("Consent successfully submitted to API.");
        return await response.json();
      }

      let errorMsg = response.statusText;
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || JSON.stringify(errorData);
      } catch {
        // fallback if JSON parsing fails
      }
      console.error(
        `Failed to record consent (${response.status}): ${errorMsg}`
      );
    } catch (error) {
      console.error("Network error submitting consent:", error);
      // Optional: retry mechanism or local storage queue can be implemented here
    }
  }

  function dropCookie(name) {
    const paths = ["/", window.location.pathname];
    // Include the base hostname and a leading dot for subdomains
    const domains = [window.location.hostname, `.${window.location.hostname}`];

    paths.forEach((path) => {
      domains.forEach((domain) => {
        // Set the expiry date to the past to force deletion
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${path}; domain=${domain};`;
      });
    });
    // Also try without the domain attribute
    paths.forEach((path) => {
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${path};`;
    });
    console.log(`CMP: Attempted to drop cookie: ${name}`);
  }
  /**
   * Overrides the native document.cookie setter to intercept and block
   * any attempts to set a non-consented cookie, using English names as a guide.
   */
  function setupCookieInterceptor() {
    const originalDescriptor = Object.getOwnPropertyDescriptor(
      Document.prototype,
      "cookie"
    );
    const originalSetter = originalDescriptor.set;

    Object.defineProperty(Document.prototype, "cookie", {
      get: function () {
        return originalDescriptor.get.call(document);
      },
      set: function (str) {
        const name = str.split("=")[0].trim();

        // Find the category for the cookie using the English translations only
        let cookieCategory = null;
        Object.keys(translations.eng.categories).forEach((cat) => {
          const categoryData = translations.eng.categories[cat];
          if (categoryData.cookies?.some((c) => c.name === name)) {
            cookieCategory = cat;
          }
        });

        const isDeletion = str.includes("expires=Thu, 01 Jan 1970");
        if (isDeletion) {
          return originalSetter.call(document, str);
        }

        if (!cookieCategory) {
          console.warn(`CMP: Blocked unknown cookie "${name}".`);
          return;
        }

        if (cookieCategory && !consentState[cookieCategory]) {
          console.warn(
            `CMP: Blocked cookie "${name}" as category "${cookieCategory}" is not consented.`
          );
          return;
        }

        originalSetter.call(document, str);
      },
      configurable: true,
    });
  }

  /**
   * Proactively deletes all non-consented cookies on page load, based on English names.
   */
  function enforceAllCookies() {
    const allCategoryCookies = Object.values(
      translations.eng.categories
    ).flatMap((category) => category.cookies || []);

    // 1. Build a Set of names for ALL cookies that are currently CONSENTED (Essential + User Choice)
    const consentedCookieNames = new Set(
      allCategoryCookies
        .filter((cookie) => {
          // Find the category for the cookie
          let category = null;
          Object.keys(translations.eng.categories).forEach((cat) => {
            const categoryData = translations.eng.categories[cat];
            // IMPORTANT: We compare by name, not object reference, to find the category
            if (categoryData.cookies?.some((c) => c.name === cookie.name)) {
              category = cat;
            }
          });
          return category && consentState[category];
        })
        .map((cookie) => cookie.name)
    );

    // 2. Get all current cookies from the browser
    const allCurrentCookies = document.cookie
      .split(";")
      .map((c) => c.trim().split("=")[0]);

    // 3. Delete any current cookie that is NOT in the consented list
    allCurrentCookies.forEach((cookieName) => {
      if (cookieName && !consentedCookieNames.has(cookieName)) {
        // Use the generic helper to forcefully drop the cookie
        dropCookie(cookieName);
      }
    });
  }

  // --- Event Listeners ---
  $("#accept-all-btn").addEventListener("click", () => {
    Object.keys(consentState).forEach((cat) => (consentState[cat] = true));
    localStorage.setItem("cookieConsent", "all");
    saveConsentState();
    hideBanner();
    executeScripts();
    syncTogglesWithConsent();
    sendConsentToApi(websiteId);
  });

  $("#accept-essential-btn").addEventListener("click", () => {
    Object.keys(consentState).forEach(
      (cat) => (consentState[cat] = cat === "essential")
    );
    localStorage.setItem("cookieConsent", "essential");
    saveConsentState();
    hideBanner();
    executeScripts();
    syncTogglesWithConsent();
    sendConsentToApi(websiteId);
  });

  $("#cookie-settings-btn").addEventListener("click", () => {
    hideBanner();
    $("#preference-modal").classList.add("show");
    syncTogglesWithConsent();
  });

  $("#close-modal-btn").addEventListener("click", closePreferenceModal);

  $("#open-preferences-btn").addEventListener("click", () => {
    $("#preference-modal").classList.add("show");
    $("#open-preferences-btn").style.display = "none";
    syncTogglesWithConsent();
  });
  $("#language-selector-banner").addEventListener("click", (e) => {
    e.stopPropagation();
    $("#language-selector-banner").classList.toggle("open");
    $("#language-dropdown-banner").classList.toggle("show");
    $("#language-dropdown-modal").classList.remove("show");
    $("#language-selector-modal").classList.remove("open");
  });

  $("#language-selector-modal").addEventListener("click", (e) => {
    e.stopPropagation();
    $("#language-selector-modal").classList.toggle("open");
    $("#language-dropdown-modal").classList.toggle("show");
    $("#language-dropdown-banner").classList.remove("show");
    $("#language-selector-banner").classList.remove("open");
  });

  shadowRoot.addEventListener("click", function (event) {
    if (event.target.closest(".language-selector")) return;
    $("#language-dropdown-banner").classList.remove("show");
    $("#language-selector-banner").classList.remove("open");
    $("#language-dropdown-modal").classList.remove("show");
    $("#language-selector-modal").classList.remove("open");
  });

  $$(".language-option").forEach((option) => {
    option.addEventListener("click", function (e) {
      e.stopPropagation();
      setLanguage(this.dataset.lang);
      $("#language-dropdown-banner").classList.remove("show");
      $("#language-selector-banner").classList.remove("open");
      $("#language-dropdown-modal").classList.remove("show");
      $("#language-selector-modal").classList.remove("open");
    });
  });

  $$(".category-item").forEach((item) => {
    item.addEventListener("click", function () {
      $$(".category-item").forEach((i) => i.classList.remove("active"));
      this.classList.add("active");
      const lang = localStorage.getItem("selectedLanguage") || "eng";
      renderCategoryDetails(lang, this.dataset.category);
    });
  });

  $("#category-details").addEventListener("click", (e) => {
    const toggleHeader = e.target.closest(".cookie-header");
    if (toggleHeader) {
      toggleCookieInfo(toggleHeader);
      return;
    }
    const toggleSwitchEl = e.target.closest(".toggle-switch");
    if (toggleSwitchEl) toggleSwitch(toggleSwitchEl);
  });

  $(".btn-reject").addEventListener("click", () => {
    Object.keys(consentState).forEach(
      (cat) => (consentState[cat] = cat === "essential")
    );
    enforceAllCookies();
    localStorage.setItem("cookieConsent", "custom");
    saveConsentState();
    closePreferenceModal();
    executeScripts();
    syncTogglesWithConsent();
    sendConsentToApi(websiteId);
  });

  $(".btn-allow").addEventListener("click", () => {
    Object.keys(consentState).forEach((cat) => (consentState[cat] = true));
    localStorage.setItem("cookieConsent", "custom");
    saveConsentState();
    closePreferenceModal();
    executeScripts();
    syncTogglesWithConsent();
  });

  $(".btn-confirm").addEventListener("click", () => {
    localStorage.setItem("cookieConsent", "custom");
    saveConsentState();

    enforceAllCookies();

    closePreferenceModal();
    executeScripts();
    syncTogglesWithConsent();
    sendConsentToApi(websiteId);
  });

  // --- Init ---
  setupCookieInterceptor();

  const savedLang = localStorage.getItem("selectedLanguage") || "eng";
  setLanguage(savedLang);

  enforceAllCookies();

  if (!localStorage.getItem("cookieConsent")) {
    showBanner();
  } else {
    hideBanner();
    consentState = initConsentState();
    executeScripts();
    syncTogglesWithConsent();
  }
}
