def domain_matches(domain: str, rules: list[tuple[str, bool]]) -> bool:
  for rule_domain, include_subdomains in rules:
    if domain == rule_domain:
      return True
    if include_subdomains and domain.endswith(f'.{rule_domain}'):
      return True
  return False
