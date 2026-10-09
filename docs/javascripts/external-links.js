/* global document$ */

document$.subscribe(() => {
  document.querySelectorAll('.md-content a[href]').forEach((link) => {
    if (
      link.closest('.md-content__button') ||
      link.closest('.md-content__button--edit') ||
      link.closest('.md-content__button--view')
    ) {
      return;
    }
    
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
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="m216-160-56-56 464-464H360v-80h400v400h-80v-264L216-160Z"/></svg>
        `;

        link.appendChild(icon);
      }
    }
  });
});