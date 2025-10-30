# onvif/utils/parser.py

import logging
from typing import List, Dict, Optional
from zeep import Plugin

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ONVIFParser(Plugin):
    """
    Lightweight Zeep plugin to extract XML elements from SOAP responses using XPath.

    This plugin extracts specific XML elements from raw SOAP responses before zeep
    parses them into Python objects. This is useful for extracting data that zeep
    doesn't parse correctly, such as simpleContent elements with attributes (e.g., Topic).

    Unlike XMLCapturePlugin which stores full XML history in memory, ONVIFParser only
    extracts and caches specified element texts from the last response.

    Usage Example 1 - Extract Topic from event notifications:
        >>> from onvif import ONVIFClient
        >>> from onvif.utils import ONVIFParser
        >>>
        >>> # Create parser to extract Topic elements
        >>> parser = ONVIFParser(extract_xpaths={
        ...     'topic': './/{http://docs.oasis-open.org/wsn/b-2}Topic'
        ... })
        >>>
        >>> # Pass parser to client as plugin
        >>> client = ONVIFClient(host, port, user, pass, plugins=[parser])
        >>>
        >>> # Make SOAP call
        >>> pullpoint = client.pullpoint(subscription)
        >>> msgs = pullpoint.PullMessages(Timeout="PT5S", MessageLimit=10)
        >>>
        >>> # Extract topic texts (cache auto-cleared on next SOAP call)
        >>> topics = parser.get_extracted_texts('topic', count=10)
        >>> for topic in topics:
        ...     print(f"Topic: {topic}")

    Usage Example 2 - Extract multiple elements:
        >>> parser = ONVIFParser(extract_xpaths={
        ...     'topic': './/{http://docs.oasis-open.org/wsn/b-2}Topic',
        ...     'custom': './/ns:CustomElement'
        ... })
        >>> client = ONVIFClient(host, port, user, pass, plugins=[parser])
        >>>
        >>> # After SOAP call
        >>> topics = parser.get_extracted_texts('topic', count=5)
        >>> customs = parser.get_extracted_texts('custom', count=5)

    Notes:
        - Uses ingress() hook to access raw XML before zeep parsing
        - Cache automatically cleared on each SOAP response
        - Thread-safe for single client usage
        - Works with any XPath expression
    """

    def __init__(self, extract_xpaths: Dict[str, str]):
        """
        Initialize XML element parser.

        Args:
            extract_xpaths: Dictionary mapping names to XPath expressions. XPath expressions will be used to find elements in SOAP response.
            Example: {
                'topic': './/{http://docs.oasis-open.org/wsn/b-2}Topic',
                'custom': './/ns:CustomElement'
            }
        """
        self.extract_xpaths = extract_xpaths
        self._extracted_elements = {}

        logger.debug(
            f"ONVIFParser initialized with XPaths: {list(extract_xpaths.keys())}"
        )

    def ingress(self, envelope, http_headers, operation):
        """
        Zeep plugin hook - called when SOAP response is received.

        Extracts element texts from raw XML envelope using configured XPath expressions.
        The envelope at this stage is an lxml Element tree, allowing XPath queries.

        Cache is automatically cleared before extracting new elements to prevent memory accumulation.

        Args:
            envelope: lxml Element representing SOAP envelope
            http_headers: HTTP response headers
            operation: Zeep operation being executed

        Returns:
            Tuple of (envelope, http_headers) to pass to next plugin
        """
        # Auto-clear cache from previous response
        self._extracted_elements = {}

        try:
            # Extract elements using XPath from raw XML envelope
            for name, xpath in self.extract_xpaths.items():
                elements = envelope.findall(xpath)

                # Extract text content from found elements
                texts = [elem.text for elem in elements if elem.text]

                if texts:
                    self._extracted_elements[name] = texts
                    logger.debug(
                        f"ONVIFParser: Extracted {len(texts)} '{name}' elements"
                    )

        except Exception as e:
            logger.warning(f"ONVIFParser: Failed to extract elements: {e}")

        return envelope, http_headers

    def get_extracted_texts(self, name: str, count: int) -> List[Optional[str]]:
        """
        Get extracted element texts by name.

        Args:
            name: Name of the extracted elements (key from extract_xpaths dict)
            count: Number of elements to return

        Returns:
            List of element text values, padded with None if fewer elements were found.
            Example: If 3 elements found but count=5, returns [text1, text2, text3, None, None]
        """
        texts = self._extracted_elements.get(name, [])[:count]

        # Pad with None if not enough elements
        while len(texts) < count:
            texts.append(None)

        return texts
