# Workload Identity Federation Troubleshooting

## Current Issue

**Status**: Workload Identity Pool created successfully ✅  
**Issue**: Cannot create OIDC Provider - getting error about attribute conditions

### Error Message
```
ERROR: (gcloud.iam.workload-identity-pools.providers.create-oidc) INVALID_ARGUMENT: 
The attribute condition must reference one of the provider's claims.
```

### What We've Tried
1. ✅ Created Workload Identity Pool: `github-actions`
2. ❌ Creating OIDC Provider with various configurations:
   - With `attribute.repository` mapping
   - Without `attribute.repository` mapping  
   - With `--attribute-condition="true"`
   - Without `--attribute-condition` flag
   - With minimal `google.subject=assertion.sub` only

All attempts result in the same error.

### Possible Causes
1. **Organization Policy**: There may be an organization policy that automatically adds attribute conditions
2. **Default Conditions**: The pool or project may have default conditions that conflict
3. **API Version Issue**: There might be a version mismatch in the gcloud CLI

### Next Steps to Try

1. **Check Organization Policies**:
   ```bash
   gcloud resource-manager org-policies list --project=p-power-up-ai
   ```

2. **Try Using REST API Directly**:
   ```bash
   # Get access token
   gcloud auth print-access-token
   
   # Then use curl to create provider with full control
   ```

3. **Check if Provider Already Exists** (maybe partially created):
   ```bash
   gcloud iam workload-identity-pools providers list \
     --location=global \
     --workload-identity-pool=github-actions \
     --project=p-power-up-ai
   ```

4. **Contact Google Cloud Support** - This appears to be a platform/configuration issue

### Workaround

For now, we can use the existing service account key approach:
- The workflows already support both WIF and service account keys
- If you have the original key file, add it as `GCP_SA_KEY` secret
- WIF can be set up later once this issue is resolved

### Resources
- Error documentation: https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines#conditions
- GitHub Actions setup: https://github.com/google-github-actions/auth#setting-up-workload-identity-federation

---

**Date**: December 24, 2024  
**Pool Created**: ✅ `projects/189514741256/locations/global/workloadIdentityPools/github-actions`  
**Provider Status**: ❌ Cannot create due to attribute condition error

