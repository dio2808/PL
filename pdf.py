from google.adk.agents import Agent, RootAgent

# ==========================
# Paste all your GCP error content here
# ==========================
DOCUMENT = """
Authentication / IAM:
- AccessDenied … storage.objects.get: Give user Project Viewer + Cloud Build Editor roles or use a dedicated logs bucket with correct permissions.
- Missing necessary permission iam.serviceAccounts.actAs: Grant iam.serviceAccounts.actAs permission between accounts.
- Unauthenticated (long-running Docker push/pull): Use custom token with sufficient lifespan.
- Cloud Build logs not visible: Grant Storage Object Viewer or Project Viewer role.

Deployment / Authentication / IAM:
- cloudfunctions.functions.get denied: Add Cloud Functions Developer role to build SA.
- cloudbuild.builds.create denied: Grant Cloud Build SA role or specific permission to create builds.
- Cloud Build SA cannot get build: Grant cloudbuild.builds.get permission.
- Permission error deploying to Cloud Run: Add cloudbuild.builds.get or Viewer/Editor roles.

Configuration / Trigger:
- Failed to trigger build: Couldn't read commit; verify trigger branch, repo, commit SHA, and trigger config.
- Request is prohibited by organization's policy: Temporarily allow Pub/Sub, create trigger, then reapply org policy.
- Secure Source Manager: “Build cannot be created”: Validate triggers.yaml; ensure SSM and Build SA have correct IAM.
- Cross-project trigger creation failing: Grant tokenAccessor role or recreate trigger with correct IAM.
- 404 : Requested entity was not found: Double-check source location, triggers, config files, IAM.

Build / Runtime / Dependency:
- docker build failed: failed to solve: file not found: Check Dockerfile paths and build context.
- Compilation failed: symbol not found: Update dependency versions; sync build tools.
- Cannot read property 'xyz' of undefined: Ensure environment variables exist and build script passes them.
- Container failed to start: PORT env variable not set: Modify code to listen on process.env.PORT.
- CrashLoopBackOff: Add required secrets, confirm network access, check env vars.
- ImagePullBackError: Grant Artifact Registry read permission to build SA.
- Internal Error (status = INTERNAL_ERROR): Retry build; check quota usage; file support ticket if persistent.
- Error response: i/o timeout (docker pull): Pre-pull image using crane or configure proxy / network.

Test / Assertion:
- jest: command not found: Install dev dependencies in build or run tests inside build environment.
- pytest failed: database connection refused: Use additional build step or service to run DB during test stage.
- JUnit test failed: null pointer: Debug test locally, mock dependencies, ensure env variables.

Upload / Artifact:
- denied: Permission denied to access repository: Add roles/artifactregistry.writer to Cloud Build SA.
- Object upload failed: 403 Forbidden: Assign roles/storage.objectAdmin or bucket ACL.
- Artifact Registry upload denied on function deploy: Grant Artifact Registry write permission to Cloud Build SA.
- Accessing private GCS fails: Use GCS client library or authorized requests.

Networking / Private Pool:
- Unable to connect … no route to host: Use non-overlapping IP range for private pool.
- Failed to connect to <external_domain>: Connection timed out: Assign external IPs to pool or configure NAT for external access.
- Timeout - last error: dial tcp i/o timeout: Fix VPC peering, firewall, routing; configure private pool internal access.
- Builds stuck / queued in private pool: Fix VPC peering or recreate private pool.

Quota / Resource:
- Quota restrictions, cannot run builds in this region: Request quota increase or use supported region.
- App Engine: Max instances exceeded: Lower max_instances or delete old versions.
- Region quota exceeded: Check quotas in GCP Console; request increase.

Other / Misc:
- Placeholder image deployed on Cloud Run: Reconfigure CD trigger; check trigger setup and permissions.
- Unexpected error for Firebase Function: Fix IAM permissions; check build config; ensure correct registry path.
- Approving old builds fails: Re-submit a new build instead of approving old one.
- UI / console missing builds: Try CLI; check IAM; clear browser cache.
- Build cannot be canceled: Use CLI cancel; contact support if persists.
- Flaky build / inconsistent errors: Retry builds; monitor memory/CPU; consider different machine type.
- App Engine node build fails (tsconfig missing): Include tsconfig.json in build context; avoid ignoring necessary files.
- App Engine: Duplicate tags not allowed: Remove or correct instance_tag in app.yaml.
- App Engine: Build succeeds but logs missing: Use Google-managed encryption keys; adjust retention policy.
"""

# ==========================
# Create the agent
# ==========================
agent = Agent(
    name="GCP Build Error Assistant",
    instruction=(
        "You are a helpful assistant. Answer ONLY based on the DOCUMENT below. "
        "If the answer is not in the text, respond: 'I couldn't find that in the document.'\n\n"
        f"DOCUMENT:\n{DOCUMENT}"
    ),
    model="gemini-2.5-flash"
)

# ==========================
# Wrap as RootAgent for ADK Web
# ==========================
root_agent = RootAgent(agent=agent)
