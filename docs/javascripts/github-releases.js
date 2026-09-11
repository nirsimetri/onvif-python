/* global marked, document$ */

const GITHUB_API =
  "https://api.github.com/repos/nirsimetri/onvif-python/releases?per_page=5";

let releases = [];

async function loadReleases() {
  const response = await fetch(GITHUB_API);

  if (!response.ok) {
    throw new Error(`GitHub API returned ${response.status}`);
  }

  return response.json();
}

function createReleaseNav(releases) {
  const navList = document.querySelector(".md-nav--primary > .md-nav__list");

  if (!navList) {
    return;
  }

  // Prevent duplicates when Material instant navigation runs.
  if (document.querySelector(".github-releases-nav")) {
    return;
  }

  const releaseItem = document.createElement("li");
  releaseItem.className = "md-nav__item md-nav__item--section github-releases-nav";

  const releaseLink = document.createElement("a");
  releaseLink.className = "md-nav__link";
  releaseLink.href = "#releases";

  const releaseTitle = document.createElement("span");
  releaseTitle.className = "md-ellipsis";
  releaseTitle.textContent = "Releases";

  releaseLink.appendChild(releaseTitle);
  releaseItem.appendChild(releaseLink);

  const releaseNav = document.createElement("nav");
  releaseNav.className = "md-nav";
  releaseNav.setAttribute("data-md-level", "1");

  const releaseList = document.createElement("ul");
  releaseList.className = "md-nav__list";

  for (const release of releases) {
    const item = document.createElement("li");
    item.className = "md-nav__item";

    const link = document.createElement("a");
    link.className = "md-nav__link";

    link.href = `/onvif-python/releases/#${encodeURIComponent(release.tag_name)}`;

    const title = document.createElement("span");
    title.className = "md-ellipsis";
    title.textContent = release.tag_name;

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
  releaseItem.appendChild(releaseNav);

  navList.appendChild(releaseItem);
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
      <h2>
        ${release.name || release.tag_name}
      </h2>

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
    releases = await loadReleases();

    createReleaseNav(releases);
    renderRelease(releases);
  } catch (error) {
    console.error("Failed to load GitHub releases:", error);

    const container = document.getElementById("github-releases");

    if (container) {
      container.innerHTML = `
        <p>Failed to load releases from GitHub.</p>
      `;
    }
  }
}

if (typeof document$ !== "undefined") {
  document$.subscribe(() => {
    initializeReleases();
  });
} else {
  document.addEventListener("DOMContentLoaded", initializeReleases);
}

window.addEventListener("hashchange", () => {
  if (releases.length) {
    renderRelease(releases);
  }
});

document.addEventListener("click", (event) => {
  const link = event.target.closest(
    ".github-releases-nav a[href*='/releases/#']"
  );

  if (!link || !releases.length) {
    return;
  }

  const url = new URL(link.href);
  const tag = decodeURIComponent(url.hash.substring(1));

  // Let Material handle the navigation first.
  setTimeout(() => {
    renderRelease(releases, tag);
  }, 0);
});

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