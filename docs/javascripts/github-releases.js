 /* global DOMPurify, marked, document$, GITHUB_REPOSITORY */

const GITHUB_REPOSITORY = "nirsimetri/onvif-python";
const [, GITHUB_REPOSITORY_NAME] = GITHUB_REPOSITORY.split("/");
const GITHUB_API = `https://api.github.com/repos/${GITHUB_REPOSITORY}/releases?per_page=100`;

const RELEASES_NAV_STATE_KEY = "github-releases-nav-open";

let releases = [];
let releasesLoaded = false;
let releasesLoading = null;
let pendingReleaseTag = null;

async function loadReleases() {
  if (releasesLoaded) {
    return releases;
  }

  if (releasesLoading) {
    return releasesLoading;
  }

  releasesLoading = fetch(GITHUB_API)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`GitHub API returned ${response.status}`);
      }

      return response.json();
    })
    .then((data) => {
      releases = data;
      releasesLoaded = true;

      return releases;
    })
    .finally(() => {
      releasesLoading = null;
    });

  return releasesLoading;
}

function createReleaseNav(releases) {
  const navList = document.querySelector(
    ".md-nav--primary > .md-nav__list"
  );

  if (!navList) {
    return;
  }

  if (navList.querySelector(".github-releases-nav")) {
    return;
  }

  const releaseItem = document.createElement("li");

  releaseItem.className =
    "md-nav__item md-nav__item--pruned github-releases-nav";

  const toggleId = "__nav_releases";

  const toggle = document.createElement("input");

  toggle.className = "md-nav__toggle md-toggle";
  toggle.type = "checkbox";
  toggle.id = toggleId;

  const releaseLabel = document.createElement("label");

  releaseLabel.className = "md-nav__link";
  releaseLabel.htmlFor = toggleId;

  const releaseTitle = document.createElement("span");

  releaseTitle.className = "md-ellipsis";
  releaseTitle.textContent = "Releases";

  const releaseIcon = document.createElement("span");

  releaseIcon.className = "md-nav__icon md-icon";

  releaseLabel.appendChild(releaseTitle);
  releaseLabel.appendChild(releaseIcon);

  const releaseNav = document.createElement("nav");

  releaseNav.className = "md-nav";
  releaseNav.setAttribute("data-md-level", "1");
  releaseNav.setAttribute("aria-labelledby", `${toggleId}_label`);
  releaseNav.setAttribute("aria-expanded", "false");

  const releaseNavTitle = document.createElement("label");

  releaseNavTitle.className = "md-nav__title";
  releaseNavTitle.htmlFor = toggleId;

  const releaseNavIcon = document.createElement("span");

  releaseNavIcon.className = "md-nav__icon md-icon";

  releaseNavTitle.appendChild(releaseNavIcon);
  releaseNavTitle.append("Releases");

  releaseNav.appendChild(releaseNavTitle);

  const releaseList = document.createElement("ul");

  releaseList.className = "md-nav__list";

  for (const release of releases) {
    const item = document.createElement("li");

    item.className = "md-nav__item";

    const link = document.createElement("a");

    link.className = "md-nav__link";
    link.href = `/${GITHUB_REPOSITORY_NAME}/releases/#${encodeURIComponent(
      release.tag_name
    )}`;

    const title = document.createElement("span");
    title.className = "md-ellipsis";
    title.textContent = release.tag_name.replace("v", "");

    const date = document.createElement("small");
    date.className = "github-release__date_title";

    const publishedAt = new Date(release.published_at);

    date.textContent = formatReleaseDate(publishedAt);

    title.append(" ", date);
    link.appendChild(title);
    item.appendChild(link);
    releaseList.appendChild(item);
  }

  const allReleasesItem = document.createElement("li");

  allReleasesItem.className = "md-nav__item";

  const allReleasesLink = document.createElement("a");

  allReleasesLink.className = "md-nav__link";
  allReleasesLink.href = `https://github.com/${GITHUB_REPOSITORY}/releases`;
  allReleasesLink.target = "_blank";
  allReleasesLink.rel = "noopener noreferrer";

  const allReleasesTitle = document.createElement("span");

  allReleasesTitle.className = "md-ellipsis";
  allReleasesTitle.textContent = "All releases";

  allReleasesLink.appendChild(allReleasesTitle);
  allReleasesItem.appendChild(allReleasesLink);
  releaseList.appendChild(allReleasesItem);

  releaseNav.appendChild(releaseList);

  releaseItem.appendChild(toggle);
  releaseItem.appendChild(releaseLabel);
  releaseItem.appendChild(releaseNav);

  navList.appendChild(releaseItem);
}

function restoreReleaseNavState() {
  const toggle = document.getElementById("__nav_releases");

  if (!toggle) {
    return;
  }

  toggle.checked = sessionStorage.getItem(RELEASES_NAV_STATE_KEY) === "true";
}

function renderRelease(releases, tag = null) {
  const container = document.getElementById("github-releases");

  if (!container) {
    return;
  }

  const releaseTag =
    tag ?? decodeURIComponent(window.location.hash.substring(1));

  const release =
    releases.find((item) => item.tag_name === releaseTag) || releases[0];

  if (!release) {
    const message = document.createElement("p");
    message.textContent = "No releases found.";

    container.replaceChildren(message);
    return;
  }

  const article = document.createElement("article");
  article.className = "github-release";

  const heading = document.createElement("h1");
  heading.append(document.createTextNode(release.tag_name.replace("v", "")));

  const latestRelease = releases.find(
    (item) => !item.draft && !item.prerelease
  );

  if (latestRelease?.id === release.id) {
    const badge = document.createElement("span");
    badge.className = "github-release__badge";
    badge.textContent = "Latest";

    heading.append(" ", badge);
  }

  const dateHeading = document.createElement("h1");
  dateHeading.className = "github-release__date_header";

  const date = document.createElement("small");

  const publishedAt = new Date(release.published_at);
  date.textContent = formatReleaseDate(publishedAt)

  dateHeading.appendChild(date);

  const header = document.createElement("div");
  header.className = "github-release__header";

  header.appendChild(heading);
  header.appendChild(dateHeading);

  const hr = document.createElement("hr");

  const metadata = document.createElement("div");
  metadata.className = "github-release__metadata";

  const author = document.createElement("span");
  author.className = "github-release__author";

  const username = release.author?.login;

  author.textContent = username
    ? `@${username} released this `
    : "Released ";

  const time = document.createElement("time");
  time.className = "github-release__time";
  time.dateTime = release.published_at;
  time.textContent = formatRelativeTime(release.published_at);

  author.appendChild(time);

  const releaseLink = document.createElement("a");
  releaseLink.className = "github-release__link";
  
  const releaseUrl = new URL(release.html_url);
  if (
    releaseUrl.protocol === "https:" &&
    releaseUrl.hostname === "github.com"
  ) {
    releaseLink.href = releaseUrl.href;
  } else {
    releaseLink.removeAttribute("href");
  }

  releaseLink.target = "_blank";
  releaseLink.rel = "noopener noreferrer";
  releaseLink.textContent = "Go to release";
  releaseLink.dataset.tooltip = "View release on GitHub";

  metadata.append(author, releaseLink);

  const body = document.createElement("div");
  body.className = "github-release__body";

  const markdownHtml = marked.parse(
    processGitHubReferences(release.body || "", release.tag_name)
  );

  const safeFragment = DOMPurify.sanitize(markdownHtml, {
    RETURN_DOM_FRAGMENT: true,
  });

  convertGitHubAlerts(safeFragment);

  body.appendChild(safeFragment);

  body.querySelectorAll("a[href]").forEach((link) => {
    link.target = "_blank";
    link.rel = "noopener noreferrer";

    const url = new URL(link.href);

    if (url.hostname !== "github.com") {
      return;
    }

    const match = url.pathname.match(
      /^\/([^/]+)\/([^/]+)\/(pull|issues)\/(\d+)\/?$/
    );

    if (match) {
      const [, , , type, number] = match;
      link.dataset.tooltip =
        type === "pull"
          ? `Pull Request #${number}`
          : `Issue #${number}`;

      return;
    }

    const commitMatch = url.pathname.match(
      /^\/([^/]+)\/([^/]+)\/commit\/([a-f0-9]{7,40})\/?$/i
    );

    if (commitMatch) {
      link.dataset.tooltip = `Commit ${commitMatch[3].slice(0, 7)}`;
      return;
    }

    const profileMatch = url.pathname.match(/^\/([a-zA-Z0-9-]+)\/?$/);

    if (profileMatch) {
      link.dataset.tooltip = `GitHub user @${profileMatch[1]}`;
    }

    const compareMatch = url.pathname.match(
      /^\/([^/]+)\/([^/]+)\/compare\/([^/]+)\.\.\.([^/]+)\/?$/
    );

    if (compareMatch) {
      const [, , , base, head] = compareMatch;
      link.dataset.tooltip = `Compare ${base} → ${head}`;
      return;
    }

    const repositoryMatch = url.pathname.match(
      /^\/([^/]+)\/([^/]+)\/?$/
    );

    if (repositoryMatch) {
      const [, owner, repo] = repositoryMatch;
      link.dataset.tooltip = `GitHub repository ${owner}/${repo}`;
      return;
    }

    const actionRunMatch = url.pathname.match(
      /^\/([^/]+)\/([^/]+)\/actions\/runs\/(\d+)\/?$/
    );

    if (actionRunMatch) {
      link.dataset.tooltip = `GitHub Actions Run #${actionRunMatch[3]}`;
      return;
    }
  });

  article.appendChild(header);
  article.appendChild(hr);
  article.appendChild(metadata);
  article.appendChild(body);

  container.replaceChildren(article);
}

function formatReleaseDate(dateString) {
  return new Date(dateString).toLocaleDateString(navigator.language, {
    year: "numeric",
    month: "long",
    day: "2-digit",
  });
}

function formatRelativeTime(dateString) {
  const date = new Date(dateString);
  const seconds = Math.floor((date.getTime() - Date.now()) / 1000);
  const units = [
    ["year", 365 * 24 * 60 * 60],
    ["month", 30 * 24 * 60 * 60],
    ["week", 7 * 24 * 60 * 60],
    ["day", 24 * 60 * 60],
    ["hour", 60 * 60],
    ["minute", 60],
  ];

  for (const [unit, secondsPerUnit] of units) {
    if (Math.abs(seconds) >= secondsPerUnit) {
      return new Intl.RelativeTimeFormat(navigator.language, {
        numeric: "auto",
      }).format(Math.round(seconds / secondsPerUnit), unit);
    }
  }

  return "just now";
}

function updateReleaseTOC() {
  const body = document.querySelector(".github-release__body");
  const nav = document.querySelector(
    ".md-sidebar--secondary .md-nav--secondary"
  );

  if (!body || !nav) {
    return;
  }

  // Create the TOC title if it doesn't exist.
  let title = nav.querySelector(":scope > .md-nav__title");

  if (!title) {
    title = document.createElement("label");
    title.className = "md-nav__title";
    title.htmlFor = "__toc";

    const icon = document.createElement("span");
    icon.className = "md-nav__icon md-icon";

    title.appendChild(icon);
    title.append(" Table of contents");
    nav.prepend(title);
  }

  // Create the root TOC list if it doesn't exist.
  let toc = nav.querySelector(":scope > .md-nav__list");

  if (!toc) {
    toc = document.createElement("ul");
    toc.className = "md-nav__list";
    toc.dataset.mdComponent = "toc";
    nav.appendChild(toc);
  }

  const headings = body.querySelectorAll("h2, h3, h4");
  const usedIds = new Set();
  const stack = [{ level: 1, list: toc }];

  toc.replaceChildren();

  headings.forEach((heading, index) => {
    const base =
      heading.textContent
        .trim()
        .toLowerCase()
        .replace(/[^\w\s-]/g, "")
        .replace(/\s+/g, "-") || `section-${index + 1}`;

    let id = base;
    let suffix = 1;

    while (
      usedIds.has(id) ||
      (document.getElementById(id) &&
        document.getElementById(id) !== heading)
    ) {
      id = `${base}-${suffix++}`;
    }

    usedIds.add(id);
    heading.id = id;

    const level = Number(heading.tagName.substring(1));

    // Find the parent list for this heading level.
    while (stack.length > 1 && stack.at(-1).level >= level) {
      stack.pop();
    }

    const parentList = stack.at(-1).list;

    const item = document.createElement("li");
    item.className = "md-nav__item";

    const link = document.createElement("a");
    link.className = "md-nav__link";
    link.href = `#${encodeURIComponent(id)}`;

    const text = document.createElement("span");
    text.className = "md-ellipsis";
    text.textContent = heading.textContent.trim();

    link.appendChild(text);

    link.addEventListener("click", (event) => {
      event.preventDefault();

      heading.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });

    item.appendChild(link);
    parentList.appendChild(item);

    // Create a nested navigation list for child headings.
    const childList = document.createElement("ul");
    childList.className = "md-nav__list";

    const childNav = document.createElement("nav");
    childNav.className = "md-nav";
    childNav.setAttribute(
      "aria-label",
      heading.textContent.trim()
    );

    childNav.appendChild(childList);
    item.appendChild(childNav);

    stack.push({ level, list: childList });
  });

  // Remove empty child navigation lists.
  toc.querySelectorAll("li").forEach((item) => {
    const childNav = item.querySelector(":scope > nav.md-nav");

    if (childNav && !childNav.querySelector(".md-nav__item")) {
      childNav.remove();
    }
  });

  nav.hidden = headings.length === 0;
}

async function initializeReleases() {
  try {
    const data = await loadReleases();

    createReleaseNav(data);
    restoreReleaseNavState();
    updateActiveReleaseLink();

    const container = document.getElementById("github-releases");

    if (!container) {
      return;
    }

    const tag =
      pendingReleaseTag ??
      decodeURIComponent(window.location.hash.substring(1));

    const { default: markedAlert } = await import(
      "https://cdn.jsdelivr.net/npm/marked-alert@2.1.2/+esm"
    );

    marked.use(markedAlert());

    renderRelease(data, tag || null);
    updateReleaseTOC();

    pendingReleaseTag = null;
    updateActiveReleaseLink();

    setTimeout(() => {
      window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    }, 100);

    updateReleaseNavigationState();
  } catch (error) {
    console.error("Failed to load GitHub releases:", error);

    const container = document.getElementById("github-releases");

    if (container) {
      const message = document.createElement("p");
      message.textContent = "Failed to load releases from GitHub.";
      container.replaceChildren(message);
    }
  }
}

function convertGitHubAlerts(fragment) {
  const alertTypes = [
    "note",
    "tip",
    "important",
    "warning",
    "caution",
  ];

  fragment.querySelectorAll(".markdown-alert").forEach((alert) => {
    const type = alertTypes.find((name) =>
      alert.classList.contains(`markdown-alert-${name}`),
    );

    if (!type) {
      return;
    }

    alert.className = `admonition ${type}`;

    const title = alert.querySelector(".markdown-alert-title");

    if (title) {
      title.className = "admonition-title";
      title.querySelectorAll("svg").forEach((svg) => svg.remove());
      title.textContent = title.textContent.trim();
    }
  });
}


function updateReleaseNavigationState() {
  const path = window.location.pathname.replace(/\/+$/, "");
  const isReleasesPage = path.endsWith("/releases");

  const placeholder = document.querySelector(
    '.md-nav--primary > .md-nav__list > .md-nav__item > a[href$="/releases/"]'
  )?.parentElement;

  const releaseNav = document.querySelector(
    ".github-releases-nav"
  );

  if (!placeholder || !releaseNav) {
    return;
  }

  placeholder.classList.toggle(
    "md-nav__item--active",
    !isReleasesPage
  );

  releaseNav.classList.toggle(
    "md-nav__item--active",
    isReleasesPage
  );

  releaseNav.classList.toggle(
    "md-nav__item--pruned",
    !isReleasesPage
  );

  const placeholderLink = placeholder.querySelector(
    ":scope > a.md-nav__link"
  );

  if (placeholderLink) {
    placeholderLink.classList.toggle(
      "md-nav__link--active",
      !isReleasesPage
    );
  }

  releaseNav.querySelectorAll(".md-nav__link").forEach((link) => {
    const isActive =
      isReleasesPage &&
      new URL(link.href, window.location.href).hash ===
        window.location.hash &&
      new URL(link.href, window.location.href).pathname ===
        window.location.pathname;

    link.classList.toggle("md-nav__link--active", isActive);
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(() => {
    initializeReleases();
  });
} else {
  document.addEventListener("DOMContentLoaded", () => {
    initializeReleases();
  });
}

window.addEventListener("hashchange", () => {
  const releasesPageContainer = document.getElementById("github-releases");
  if (releasesLoaded && releasesPageContainer) {
    renderRelease(releases);
    setTimeout(() => {
      window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    }, 50);
  }
  setTimeout(updateActiveReleaseLink, 10);
});

document.addEventListener("change", (event) => {
  if (event.target.id === "__nav_releases") {
    sessionStorage.setItem(
      RELEASES_NAV_STATE_KEY,
      String(event.target.checked)
    );
  }
});

document.addEventListener("click", (event) => {
  const releasesNav = document.querySelector(".github-releases-nav");
  const toggle = document.getElementById("__nav_releases");

  if (!releasesNav || !toggle || !toggle.checked) {
    return;
  }

  const clickedInsideReleases = releasesNav.contains(event.target);
  const clickedInPrimaryNav = event.target.closest(".md-nav--primary") !== null;

  if (!clickedInsideReleases && clickedInPrimaryNav) {
    toggle.checked = false;
    sessionStorage.setItem(RELEASES_NAV_STATE_KEY, "false");
  }
}, true);

function updateActiveReleaseLink() {
  const releaseLinks = document.querySelectorAll(
    ".github-releases-nav a[href*='/releases/#']"
  );

  const path = window.location.pathname.replace(/\/+$/, "");
  const isReleasesPage = path.endsWith("/releases");

  const currentTag = window.location.hash
    ? decodeURIComponent(window.location.hash.slice(1))
    : isReleasesPage
      ? releases[0]?.tag_name
      : null;

  releaseLinks.forEach((link) => {
    const linkTag = decodeURIComponent(
      new URL(link.href).hash.slice(1)
    );

    const isActive =
      isReleasesPage &&
      currentTag !== null &&
      linkTag === currentTag;

    const item = link.closest("li");

    item?.classList.toggle("md-nav__item--active", isActive);
    link.classList.toggle("md-nav__link--active", isActive);
  });
}

document.addEventListener("click", (event) => {
  const link = event.target.closest(
    ".github-releases-nav a[href*='/releases/#']"
  );

  if (!link) {
    return;
  }

  const releaseLinks = document.querySelectorAll(
    ".github-releases-nav a[href*='/releases/#']"
  );
  releaseLinks.forEach((l) => {
    const li = l.closest("li");
    if (li) {
      li.classList.remove("md-nav__item--active");
    }
    l.classList.remove("md-nav__link--active");
  });

  const li = link.closest("li");
  if (li) {
    li.classList.add("md-nav__item--active");
  }
  link.classList.add("md-nav__link--active");

  const url = new URL(link.href);
  pendingReleaseTag = decodeURIComponent(url.hash.substring(1));

  if (releasesLoaded) {
    setTimeout(() => {
      renderRelease(releases, pendingReleaseTag);
      updateReleaseTOC();
      pendingReleaseTag = null;
      restoreReleaseNavState();
      updateActiveReleaseLink();
      window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    }, 50);
  }
});

if (typeof document$ !== "undefined") {
  document$.subscribe(() => {
    setTimeout(updateActiveReleaseLink, 50);
  });
}

function processGitHubReferences(markdown, tag) {
  const htmlBlocks = [];

  // Protect HTML tags from Markdown URL transformations.
  let text = markdown.replace(
    /<[^>]+>/g,
    (match) => {
      const index = htmlBlocks.push(match) - 1;
      return `HTMLBLOCKPLACEHOLDER${index}END`;
    },
  );

  // Convert GitHub issue/PR URLs to # references.
  text = text.replace(
    /https:\/\/github\.com\/([^/\s]+)\/([^/\s]+)\/(issues|pull)\/(\d+)/g,
    (_, owner, repo, type, number) => {
      const repository = `${owner}/${repo}`;
      const url = `https://github.com/${repository}/${type}/${number}`;
      const label =
        repository === GITHUB_REPOSITORY
          ? `#${number}`
          : `${repository}#${number}`;

      return `[${label}](${url})`;
    },
  );

  // Convert GitHub commit URLs to short commit hashes.
  text = text.replace(
    /https:\/\/github\.com\/([^/\s]+)\/([^/\s]+)\/commit\/([a-f0-9]{7,40})/gi,
    (_, owner, repo, hash) => {
      const repository = `${owner}/${repo}`;
      const url = `https://github.com/${repository}/commit/${hash}`;
      const shortHash = hash.substring(0, 7);
      const label =
        repository === GITHUB_REPOSITORY
          ? `\`${shortHash}\``
          : `${repository}@\`${shortHash}\``;

      return `[${label}](${url})`;
    },
  );

  // Convert @username to GitHub profile links, except inside inline code.
  text = text
    .split(/(`[^`]*`)/g)
    .map((part, index) => {
      // Odd parts are inline code blocks.
      if (index % 2 === 1) {
        return part;
      }

      return part.replace(
        /(^|[^\w])@([a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)/g,
        "$1[@$2](https://github.com/$2)",
      );
    })
    .join("");

  // Convert GitHub compare URLs to version range links.
  text = text.replace(
    /https:\/\/github\.com\/([^/\s]+)\/([^/\s]+)\/compare\/([^/\s]+)\.\.\.([^/\s]+)/g,
    (_, owner, repo, base, head) => {
      const repository = `${owner}/${repo}`;
      const url = `https://github.com/${repository}/compare/${base}...${head}`;

      return repository === GITHUB_REPOSITORY
        ? `[\`${base}...${head}\`](${url})`
        : `[${repository}: \`${base}...${head}\`](${url})`;
    },
  );

  // Convert relative file links to GitHub release source links.
  text = text.replace(
    /(\[[^\]]+\])\((\.\/[^)\s]+)\)/g,
    (_, label, path) =>
      `${label}(https://github.com/${GITHUB_REPOSITORY}/blob/${tag}/${path.slice(2)})`,
  );

  // Convert plain GitHub repository URLs to Markdown links.
  text = text.replace(
    /(?<!\]\()https:\/\/github\.com\/([a-zA-Z0-9-]+)\/([a-zA-Z0-9_.-]+)\/?(?![^\s]*\))/g,
    (url, owner, repo) => `[${owner}/${repo}](${url})`,
  );

  // Restore protected HTML tags.
  text = text.replace(
    /HTMLBLOCKPLACEHOLDER(\d+)END/g,
    (_, index) => htmlBlocks[Number(index)],
  );

  return text;
}