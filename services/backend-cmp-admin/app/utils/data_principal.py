def mask_email(email) -> str:
    email_str = str(email)
    if "@" not in email_str:
        return email_str
    local, domain = email_str.split("@", 1)
    if len(local) <= 4:

        return f"{local}@{domain}"
    masked_local = local[:2] + "******" + local[-2:]
    return f"{masked_local}@{domain}"


def mask_mobile(mobile) -> str:
    mobile_str = str(mobile)

    if len(mobile_str) >= 4:
        return mobile_str[:2] + "*" * (len(mobile_str) - 4) + mobile_str[-2:]
    return mobile_str
