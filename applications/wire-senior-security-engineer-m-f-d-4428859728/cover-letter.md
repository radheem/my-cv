---
recipient: ""
company: "Wire"
---

A secure communication layer survives hostile networks only when encryption becomes the default state of every data path. I want to bring that mindset to the Senior Security Engineer role at Wire. My background in distributed systems and cloud-native infrastructure has taught me that security controls only work when they are woven into the deployment pipeline rather than bolted on afterward.

On the IRS platform, I designed a credential vault that enforced AES-256-GCM encryption for every authenticated browser session. I routed that traffic through a Cilium-powered Kubernetes mesh with strict network policies to isolate sensitive workloads. I replaced a heavy sidecar dependency with native NATS JetStream for messaging. I paired the messaging layer with a CUE-based schema contract to prevent misconfiguration drift across multiple vendor integrations. Those same principles guided my work on document protection, where I implemented PBKDF2 key derivation and in-browser AES-256-GCM encryption. I kept application artifacts sealed before they ever reached a public deployment target. I automated the entire build and verification loop with GitHub Actions. I ensured that every cryptographic dependency and container image passed reproducible regression gates before reaching production. I documented each control to support future security audits and compliance reviews.

I am ready to apply this disciplined approach to Wire’s product and platform security controls. I will help your engineering teams catch privacy pitfalls early while maintaining the performance your customers expect. I am available to start full-time immediately. I can relocate anywhere in Germany within two to three weeks. My Blue Card status requires no employer sponsorship overhead, as the company only needs to issue the employment contract. I look forward to discussing how I can contribute to your information security team.
