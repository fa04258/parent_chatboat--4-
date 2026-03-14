"""
HTML-aware translation helper.
Translates only the visible text nodes inside an HTML string,
leaving tags, attributes, and emoji intact.
"""

from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator

# Supported languages: label -> BCP-47 code
LANG_MAP = {
    "english": "en",
    "hindi":   "hi",
    "telugu":  "te",
}

# Map language code -> SpeechRecognition locale (sent to frontend)
SPEECH_LANG_MAP = {
    "en": "en-US",
    "hi": "hi-IN",
    "te": "te-IN",
}


def translate_html(html_content: str, target_label: str) -> str:
    """
    Translate the text content of *html_content* to *target_label*
    (one of 'english', 'hindi', 'telugu').
    Returns the original string unchanged if target is English or on any error.
    """
    target_code = LANG_MAP.get(target_label, "en")
    if target_code == "en" or not html_content:
        return html_content

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        translator = GoogleTranslator(source="auto", target=target_code)

        for element in soup.find_all(string=True):
            text = str(element).strip()
            # Skip empty strings and HTML comments
            if not text or text.startswith("<!--"):
                continue
            try:
                translated = translator.translate(text)
                if translated:
                    element.replace_with(translated)
            except Exception:
                pass  # Leave original text on individual failure

        return str(soup)
    except Exception:
        return html_content  # Fallback: return untranslated content
