# Azure App Registration Setup

This guide walks you through creating an Azure app registration with the permissions needed for app-only access to Microsoft Planner via the Graph API.

## Prerequisites

- An Azure account with admin access to your Microsoft Entra ID (Azure AD) tenant
- A Microsoft 365 subscription with Planner enabled

## Step 1: Register the Application

1. Go to [Azure Portal](https://portal.azure.com) > **Microsoft Entra ID** > **App registrations**
2. Click **New registration**
3. Fill in:
   - **Name:** `ms-planner-agent` (or your preferred name)
   - **Supported account types:** "Accounts in this organizational directory only" (single tenant)
   - **Redirect URI:** Leave blank (not needed for client credentials flow)
4. Click **Register**
5. Note down:
   - **Application (client) ID** — this is your `CLIENT_ID`
   - **Directory (tenant) ID** — this is your `TENANT_ID`

## Step 2: Create a Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "planner-agent-secret") and choose an expiry
4. Click **Add**
5. **Copy the secret value immediately** — it won't be shown again. This is your `CLIENT_SECRET`

## Step 3: Add API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Application permissions**
3. Search for and add:
   - `Tasks.ReadWrite.All` — required for full Planner CRUD
   - `Group.Read.All` — required to list plans by group
   - `User.Read.All` — required to list tasks by user
4. Click **Add permissions**
5. Click **Grant admin consent for [your tenant]** (requires Global Admin or Privileged Role Administrator)
6. Confirm all permissions show a green checkmark under "Status"

## Step 4: Configure Your Environment

Create a `.env` file in the project root (copy from `.env.example`):

```env
TENANT_ID=your-tenant-id-here
CLIENT_ID=your-client-id-here
CLIENT_SECRET=your-client-secret-here
```

**Never commit `.env` to git.** The `.gitignore` file already excludes it.

## Step 5: Verify

Run the CLI to verify your setup:

```bash
planner plans list --group-id <a-group-id-you-know>
```

If permissions are configured correctly, you should see the plans for that group.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| 401 Unauthorized | Bad or expired token | Check CLIENT_ID, CLIENT_SECRET, TENANT_ID |
| 403 Forbidden | Missing permissions | Ensure admin consent was granted (Step 3.5) |
| 403 on specific plan | App can't access that group | Verify the group exists and permissions are tenant-wide |
| 404 Not Found | Wrong plan/task/group ID | Double-check the ID value |

## Security Notes

- Use **certificate-based auth** instead of client secrets for production deployments
- Rotate client secrets before they expire
- Consider using Azure Key Vault to store secrets instead of `.env` files
- `Tasks.ReadWrite.All` grants access to **all** Planner data in the tenant — scope down if needed
