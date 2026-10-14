/* global document$, GITHUB_REPOSITORY */

document$.subscribe(() => {
  document.querySelectorAll('.md-content__button[href*="/raw/"]').forEach((editButton) => {
    if (editButton.parentElement.querySelector(".report-issue-button")) return;

    const issueTitle =
        document.querySelector(".md-content h1")?.textContent.trim() ||
        document.title;
    const issueBody = encodeURIComponent(
        `**Reference:** \n${window.location.href}\n\n**Description:**\n`
    );

    const reportButton = document.createElement("a");
    reportButton.className = "md-content__button md-icon report-issue-button";
    reportButton.href =
        `https://github.com/${GITHUB_REPOSITORY}/issues/new` +
        `?title=${issueTitle}&body=${issueBody}`;
    reportButton.target = "_blank";
    reportButton.rel = "noopener noreferrer";
    reportButton.dataset.tooltip = "Report an issue";
    reportButton.setAttribute("aria-label", "Report an issue");
    reportButton.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg"
           viewBox="0 0 24 24"
           aria-hidden="true">
        <path fill="currentColor"
          d="M17,14H19V17H22V19H19V22H17V19H14V17H17V14M5,3H19C20.11,3 21,3.89 21,5V12.8C20.39,12.45 19.72,12.2 19,12.08V5H5V19H12.08C12.2,19.72 12.45,20.39 12.8,21H5C3.89,21 3,20.11 3,19V5C3,3.89 3.89,3 5,3M7,7H17V9H7V7M7,11H17V12.08C16.15,12.22 15.37,12.54 14.68,13H7V11M7,15H12V17H7V15Z"/>
      </svg>
    `;

    editButton.after(reportButton);
  });
});