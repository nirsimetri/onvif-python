/* global document$ */

document$.subscribe(() => {
  document.querySelectorAll('.md-content a[href]').forEach((link) => {
    const url = new URL(link.href, window.location.href);

    const isEditButton =
      link.classList.contains('md-content__button') &&
      url.hostname === 'github.com' &&
      /\/edit\//.test(url.pathname);

    const isViewButton =
      link.classList.contains('md-content__button') &&
      url.hostname === 'github.com' &&
      /\/raw\//.test(url.pathname);

    if (isEditButton || isViewButton) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';

      link.dataset.tooltip = isEditButton
        ? 'Edit this page'
        : 'View source of this page';

      // Remove external icons from Edit and View buttons.
      link.querySelectorAll('.external-link-icon').forEach((icon) => {
        icon.remove();
      });

      return;
    }

    if (
      ['http:', 'https:'].includes(url.protocol) &&
      url.hostname !== window.location.hostname
    ) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';

      // Do not add external icons inside source-code blocks.
      if (link.closest('.highlight, .highlighttable, pre')) {
        return;
      }

      if (
        !link.classList.contains('no-external-icon') &&
        !link.querySelector('.external-link-icon')
      ) {
        const icon = document.createElement('span');
        icon.className = 'external-link-icon';
        icon.setAttribute('aria-hidden', 'true');

        icon.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960">
            <path d="m216-160-56-56 464-464H360v-80h400v400h-80v-264L216-160Z"></path>
          </svg>
        `;

        const code = link.querySelector('code');

        // Place the icon inside inline code when present.
        (code || link).appendChild(icon);
      }
    }
  });
});
