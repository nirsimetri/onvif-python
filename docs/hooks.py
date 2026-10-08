def on_page_content(html, page, config, files):
    """Exclude mkdocstrings source blocks from Material search."""
    return html.replace(
        '<details class="mkdocstrings-source">',
        '<details class="mkdocstrings-source" data-search-exclude>',
    )