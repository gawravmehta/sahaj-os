def inject_legacy_hooks(html: str) -> str:
    """Injects legacy compatibility replacements into notice HTML."""
    return html.replace("/n/submit-consent", "/ln/submit-legacy-consent")
