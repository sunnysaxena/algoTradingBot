5️⃣ Why This Approach?

✅ No Sensitive Data in YAML: Credentials are only stored in environment variables.

✅ Flexible Configuration: You can update broker settings without modifying code.

✅ Secure & Scalable: Supports multiple brokers while keeping credentials safe.

✅ Cross-Platform Support: Works on Windows, Linux, and macOS.

6️⃣ Next Steps

* If using Docker, store credentials in a .env file and load them in your container.
* If using Kubernetes, store credentials in Secrets instead of environment variables.
* If using Git, add config/broker_config.yml and .env to .gitignore to prevent accidental commits.