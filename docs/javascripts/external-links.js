/* global document$ */

document$.subscribe(() => {
  document.querySelectorAll('.md-content a[href]').forEach((link) => {
    const url = new URL(link.href, window.location.href);

    if (
      (url.protocol === "http:" || url.protocol === "https:") &&
      url.hostname !== window.location.hostname
    ) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";

      if (
        !link.classList.contains("no-external-icon") &&
        !link.querySelector(".external-link-icon")
      ) {
        const icon = document.createElement("span");
        icon.className = "external-link-icon";
        icon.setAttribute("aria-hidden", "true");

        icon.innerHTML = `
          <svg viewBox="0 0 24 24">
            <path d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42L17.59 5H14V3zM5 5h5V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-5h-2v5H5V5z"/>
          </svg>
        `;

        link.appendChild(icon);
      }
    }
  });
});