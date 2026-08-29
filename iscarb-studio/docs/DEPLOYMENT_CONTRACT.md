# Production deployment contract

The Render service deploys the `main` branch from the `iscarb-studio` root directory.

Pre-deploy GitHub checks must validate code and artifacts only. They must not wait for the live Render service to change version, because Render may be configured to deploy only after CI checks pass. Live production validation therefore runs as a separate post-deploy/manual workflow.

Release sequence:

1. Merge validated source changes to `main`.
2. Let repository CI complete successfully.
3. Render auto-deploys the changed `iscarb-studio` tree.
4. Run `ISCARB Production Validation` against multiple archived CIMT lectures.
5. A production release is accepted only when health reports v4.3.0 and the live multi-lecture validation passes.

This separation prevents a circular dependency in which production checks wait for Render while Render waits for those same checks.
