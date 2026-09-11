/* global document$ */

document$.subscribe(() => {
  document.querySelectorAll('a[href^="http"]').forEach((link) => {
    if (link.hostname !== window.location.hostname) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
  });
});