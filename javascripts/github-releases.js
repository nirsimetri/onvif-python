 /* global DOMPurify, marked, document$ */

const GITHUB_API =
  "https://api.github.com/repos/nirsimetri/onvif-python/releases";

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
    "md-nav__item md-nav__item--nested github-releases-nav";

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
    link.href = `/onvif-python/releases/#${encodeURIComponent(
      release.tag_name
    )}`;

    const title = document.createElement("span");

    const date = new Date(release.published_at);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const formattedDate = `${year}-${month}-${day}`;

    title.className = "md-ellipsis";
    title.textContent = `${release.tag_name} (${formattedDate})`;

    link.appendChild(title);
    item.appendChild(link);
    releaseList.appendChild(item);
  }

  const allReleasesItem = document.createElement("li");

  allReleasesItem.className = "md-nav__item";

  const allReleasesLink = document.createElement("a");

  allReleasesLink.className = "md-nav__link";
  allReleasesLink.href =
    "https://github.com/nirsimetri/onvif-python/releases";
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
    container.innerHTML = "<p>No releases found.</p>";
    return;
  }

  const markdownHtml = marked.parse(
    processGitHubReferences(release.body || "")
  );

  const safeHtml = DOMPurify.sanitize(markdownHtml);

  container.innerHTML = `
    <article class="github-release">
      <h2>${release.name || release.tag_name}</h2>
      <p class="github-release__date">
        ${new Date(release.published_at).toLocaleDateString()}
      </p>
      <div class="github-release__body">
        ${safeHtml}
      </div>
    </article>
  `;
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

    renderRelease(data, tag || null);

    pendingReleaseTag = null;
    updateActiveReleaseLink();
  } catch (error) {
    console.error("Failed to load GitHub releases:", error);

    const container = document.getElementById("github-releases");

    if (container) {
      container.innerHTML =
        "<p>Failed to load releases from GitHub.</p>";
    }
  }
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
  if (releasesLoaded) {
    renderRelease(releases);
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
  const currentHash = window.location.hash;

  releaseLinks.forEach((link) => {
    const url = new URL(link.href);
    const linkHash = url.hash;
    const li = link.closest("li");

    if (li) {
      li.classList.remove("md-nav__item--active");
    }
    link.classList.remove("md-nav__link--active");

    if (linkHash === currentHash) {
      if (li) {
        li.classList.add("md-nav__item--active");
      }
      link.classList.add("md-nav__link--active");
    }
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
      pendingReleaseTag = null;
      restoreReleaseNavState();
      updateActiveReleaseLink();
    }, 50);
  }
});

if (typeof document$ !== "undefined") {
  document$.subscribe(() => {
    setTimeout(updateActiveReleaseLink, 50);
  });
}

function processGitHubReferences(markdown) {
  let text = markdown;

  // Convert GitHub issue/PR URLs to # references.
  text = text.replace(
    /https:\/\/github\.com\/nirsimetri\/onvif-python\/(issues|pull)\/(\d+)/g,
    (_, type, number) =>
      `[#${number}](https://github.com/nirsimetri/onvif-python/${type}/${number})`
  );

  // Convert GitHub commit URLs to short commit hashes.
  text = text.replace(
    /https:\/\/github\.com\/nirsimetri\/onvif-python\/commit\/([a-f0-9]{7,40})/gi,
    (_, hash) =>
      `[${hash.substring(0, 7)}](https://github.com/nirsimetri/onvif-python/commit/${hash})`
  );

  // Convert @username to GitHub profile links.
  text = text.replace(
    /(^|[^\w])@([a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)/g,
    "$1[@$2](https://github.com/$2)"
  );

  return text;
}