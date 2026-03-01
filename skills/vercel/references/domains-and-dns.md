# Domains and DNS

Sources: Vercel CLI docs (2026), Vercel domain management documentation

Covers: Domain lifecycle, DNS records, SSL certificates, wildcard domains,
multi-tenant patterns, and domain operations via CLI.

## Domain Lifecycle

1. **Add** domain to project: `vercel domains add`
2. **Configure** DNS records: `vercel dns add` or external DNS provider
3. **Verify** configuration: `vercel domains inspect`
4. **Certificate** issued automatically by Vercel (Let's Encrypt)
5. **Active**: domain serves traffic from the project

## Domain Commands

### List Domains

```bash
vercel domains ls
vercel domains ls --limit 100
vercel domains ls --next 1584722256178   # Pagination token
```

### Inspect Domain

```bash
vercel domains inspect example.com
```

Shows: DNS configuration status, certificate status, project assignment,
nameserver configuration.

### Add Domain to Project

```bash
vercel domains add example.com my-project
vercel domains add example.com my-project --force  # Override existing assignment
```

A domain can only be assigned to one project at a time. Use `--force` to
reassign from another project.

### Remove Domain

```bash
vercel domains rm example.com
vercel domains rm example.com --yes      # Skip confirmation
```

### Purchase Domain

```bash
vercel domains buy example.com
```

Purchased domains are automatically configured with Vercel nameservers.

### Move Domain

Transfer domain to another team or personal account:

```bash
vercel domains move example.com target-team-slug
```

### Transfer Domain In

Transfer domain registration from another registrar:

```bash
vercel domains transfer-in example.com
```

Requires authorization code from current registrar. Domain must be unlocked.

## DNS Record Management

### List Records

```bash
vercel dns ls
vercel dns ls --limit 100
```

### Add Records

```bash
# A record (IPv4)
vercel dns add example.com www A 192.0.2.1
vercel dns add example.com '@' A 76.76.21.21     # Apex domain

# AAAA record (IPv6)
vercel dns add example.com www AAAA 2001:0db8::1

# CNAME record
vercel dns add example.com www CNAME cname.vercel-dns.com
vercel dns add example.com blog CNAME myblog.example.com

# TXT record
vercel dns add example.com '@' TXT "v=spf1 include:_spf.example.com ~all"

# MX record (with priority)
vercel dns add example.com '@' MX mail.example.com 10

# SRV record (priority weight port target)
vercel dns add example.com _sip SRV 10 60 5060 sip.example.com

# CAA record
vercel dns add example.com '@' CAA '0 issue "letsencrypt.org"'
```

### Remove Records

```bash
vercel dns rm rec_abc123def456
```

Find record IDs with `vercel dns ls`.

### Import Zonefile

```bash
vercel dns import example.com ./zonefile.txt
```

DNS changes can take up to 24 hours to propagate.

## Common Domain Setups

### Apex Domain (example.com)

```bash
# Add domain to project
vercel domains add example.com my-project

# If using Vercel nameservers: automatic
# If using external DNS: add A record
vercel dns add example.com '@' A 76.76.21.21
```

### WWW Subdomain (www.example.com)

```bash
vercel domains add www.example.com my-project

# If using external DNS: add CNAME
vercel dns add example.com www CNAME cname.vercel-dns.com
```

### Apex + WWW with Redirect

Add both domains. Configure one as primary and redirect the other:

```json
{
  "redirects": [
    {
      "source": "/:path*",
      "has": [{ "type": "host", "value": "www.example.com" }],
      "destination": "https://example.com/:path*",
      "permanent": true
    }
  ]
}
```

### Custom Subdomain (blog.example.com)

```bash
vercel domains add blog.example.com my-blog-project
vercel dns add example.com blog CNAME cname.vercel-dns.com
```

### Wildcard Domain (*.example.com)

Requires Vercel nameservers:

1. Add wildcard domain: `vercel domains add "*.example.com" my-project`
2. Add apex domain: `vercel domains add example.com my-project`
3. Point nameservers to Vercel:
   - `ns1.vercel-dns.com`
   - `ns2.vercel-dns.com`

Any subdomain (`tenant1.example.com`, `app.example.com`) automatically
resolves with a valid SSL certificate.

Cannot use wildcard domains with external DNS providers.

## Vercel Nameservers vs External DNS

| Approach | Pros | Cons |
|----------|------|------|
| Vercel nameservers | Wildcard support, automatic config, fastest propagation | Must move all DNS to Vercel |
| External DNS | Keep existing DNS provider, granular control | Manual record setup, no wildcard, slower propagation |

**Use Vercel nameservers when**: wildcard domains needed, new domain, or
willing to migrate all DNS.

**Use external DNS when**: other services share the domain, corporate DNS
policies, or only adding specific subdomains.

## SSL/TLS Certificates

Vercel automatically provisions and renews certificates via Let's Encrypt.

### Automatic Management

No action needed. Certificates are issued when a domain is added and
verified. Renewal happens automatically before expiration.

### Manual Certificate Operations

```bash
vercel certs ls                          # List all certificates
vercel certs issue example.com           # Issue certificate manually
vercel certs issue example.com www.example.com  # Multi-domain cert
vercel certs issue example.com --challenge-only  # Show DNS challenges
vercel certs rm cert_abc123              # Remove certificate
```

Use `--challenge-only` to see required DNS records without issuing.

## Multi-Tenant Domain Patterns

For platforms serving multiple tenants on custom domains:

### Programmatic Domain Management

Use the Vercel SDK to add/remove domains dynamically:

```typescript
import { VercelCore as Vercel } from "@vercel/sdk/core.js";
import { projectsAddProjectDomain } from "@vercel/sdk/funcs/projectsAddProjectDomain.js";

const vercel = new Vercel({ bearerToken: process.env.VERCEL_TOKEN });

await projectsAddProjectDomain(vercel, {
  idOrName: "my-multi-tenant-app",
  teamId: process.env.VERCEL_TEAM_ID,
  requestBody: { name: "tenant.example.com" },
});
```

### Tenant Domain Setup Flow

1. Tenant provides their custom domain in your app.
2. Your backend calls Vercel API to add the domain.
3. Show tenant the required DNS records (CNAME to `cname.vercel-dns.com`).
4. Poll domain verification status until confirmed.
5. SSL certificate is auto-provisioned.

### Wildcard for Subdomains

For subdomain-based multi-tenancy (`tenant1.myapp.com`):

1. Configure wildcard domain on Vercel.
2. Read subdomain in middleware or server component.
3. Route to tenant-specific content.

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const hostname = request.headers.get("host") || "";
  const subdomain = hostname.split(".")[0];
  // Route based on subdomain
}
```

## Custom Aliases

Assign custom URLs to specific deployments:

```bash
vercel alias set [deployment-url] custom.example.com
vercel alias rm custom.example.com
vercel alias ls
```

Use cases: preview environments with stable URLs, staging aliases,
customer-facing demo URLs.

## DNS Record Type Guide

| Need | Record Type | Example |
|------|-------------|---------|
| Point domain to Vercel (apex) | A | `@ A 76.76.21.21` |
| Point subdomain to Vercel | CNAME | `www CNAME cname.vercel-dns.com` |
| Email routing | MX | `@ MX mail.example.com 10` |
| Domain verification | TXT | `@ TXT "verify=abc123"` |
| SPF for email | TXT | `@ TXT "v=spf1 include:..."` |
| Certificate authority auth | CAA | `@ CAA '0 issue "letsencrypt.org"'` |
| Service discovery | SRV | `_sip SRV 10 60 5060 sip.example.com` |
