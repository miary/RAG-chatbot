"""Mock Guardian incident data for RAG ingestion."""

GUARDIAN_INCIDENTS = [
    {
        'id': 1,
        'title': 'Authentication Failure - Service Account Lockout',
        'content': 'Service account lockout occurs when the PSPD Guardian service account exceeds the maximum allowed failed authentication attempts. This typically happens after password rotation or when cached credentials become stale. The resolution is to reset the service account password in Active Directory, clear the cached credentials on the application server, and restart the Guardian authentication service. Check Event Viewer for Event ID 4625 to confirm lockout events.',
        'metadata': {
            'category': 'Authentication',
            'severity': 'High',
            'resolution': 'Reset service account password, clear cached credentials, restart auth service.',
            'error_code': 'AUTH-001',
        },
    },
    {
        'id': 2,
        'title': 'Database Connection Timeout - Spanner Vector Search',
        'content': 'Spanner Vector Search connection timeouts happen when the database connection pool is exhausted or when network latency between the application tier and Spanner exceeds the configured timeout threshold of 30 seconds. Resolution: increase the connection pool size in the guardian-config.yaml file, check network routes between application servers and Spanner instances, and verify that the Spanner instance is not under heavy load. Monitor the connection_pool_exhausted metric in Grafana.',
        'metadata': {
            'category': 'Database',
            'severity': 'Critical',
            'resolution': 'Increase connection pool size, check network routes, verify Spanner load.',
            'error_code': 'DB-002',
        },
    },
    {
        'id': 3,
        'title': 'API Gateway 503 Service Unavailable',
        'content': 'A 503 Service Unavailable error from the Guardian API gateway indicates that the backend services are not responding. This can be caused by: (1) Backend pod crash loops in Kubernetes, (2) Health check failures, (3) Resource limits being exceeded. To troubleshoot: check pod status with kubectl get pods -n guardian, review pod logs with kubectl logs, verify resource requests and limits in the deployment manifest, and check if horizontal pod autoscaler is functioning correctly.',
        'metadata': {
            'category': 'API',
            'severity': 'Critical',
            'resolution': 'Check pod status, review logs, verify resource limits, check HPA.',
            'error_code': 'API-503',
        },
    },
    {
        'id': 4,
        'title': 'Certificate Expiration Warning',
        'content': 'Guardian TLS certificates are issued with a 1-year validity period. When certificates are within 30 days of expiration, the system generates alerts. To renew certificates: submit a certificate signing request (CSR) through the CBP PKI portal, download the renewed certificate, update the Kubernetes secret with the new certificate and key, and perform a rolling restart of the affected deployments. Verify with openssl s_client -connect hostname:443.',
        'metadata': {
            'category': 'Security',
            'severity': 'High',
            'resolution': 'Submit CSR, download renewed cert, update K8s secret, rolling restart.',
            'error_code': 'SEC-010',
        },
    },
    {
        'id': 5,
        'title': 'Memory Leak in Guardian Processor Service',
        'content': 'The Guardian Processor service has a known memory leak issue when processing large batches of incident data exceeding 10,000 records. Memory usage gradually increases until the pod is OOMKilled. Workaround: set the BATCH_SIZE environment variable to 5000, configure memory limits to 4Gi with a request of 2Gi, and enable the memory profiler by setting ENABLE_MEM_PROFILER=true. A permanent fix is scheduled for release 4.2.1.',
        'metadata': {
            'category': 'Performance',
            'severity': 'Medium',
            'resolution': 'Reduce batch size to 5000, set memory limits, enable profiler.',
            'error_code': 'PERF-005',
        },
    },
    {
        'id': 6,
        'title': 'User Guide and Documentation Access',
        'content': 'PSPD Guardian user guides and documentation are available at the internal documentation portal: pspd-guardian-help-dev.cbp.dhs.gov. The portal contains: Getting Started guide, API reference documentation, Troubleshooting playbooks, Release notes, and Administrator configuration guides. Access requires valid CBP network credentials. For access issues, contact the Guardian support team at guardian-support@cbp.dhs.gov.',
        'metadata': {
            'category': 'Documentation',
            'severity': 'Low',
            'resolution': 'Visit pspd-guardian-help-dev.cbp.dhs.gov for documentation.',
            'error_code': 'DOC-001',
        },
    },
    {
        'id': 7,
        'title': 'Log Aggregation Pipeline Failure',
        'content': 'The Guardian log aggregation pipeline uses Fluentd to collect logs from all microservices and forward them to Elasticsearch. Pipeline failures are typically caused by: Elasticsearch cluster health turning red, Fluentd buffer overflow, or network policies blocking traffic on port 9200. Resolution: check Elasticsearch cluster health with curl localhost:9200/_cluster/health, restart Fluentd DaemonSet, verify network policies allow egress to Elasticsearch, and check disk space on Elasticsearch nodes.',
        'metadata': {
            'category': 'Logging',
            'severity': 'Medium',
            'resolution': 'Check ES health, restart Fluentd, verify network policies, check disk.',
            'error_code': 'LOG-003',
        },
    },
    {
        'id': 8,
        'title': 'Role-Based Access Control (RBAC) Permission Denied',
        'content': 'RBAC permission denied errors occur when a user attempts to access a Guardian resource without the appropriate role assignment. Common scenarios: new users not added to correct AD groups, role mapping configuration out of date, or RBAC cache not refreshed. Resolution: verify user AD group membership, check role mappings in guardian-rbac-config.yaml, clear the RBAC cache by calling POST /api/admin/rbac/refresh, and review audit logs for denied access attempts.',
        'metadata': {
            'category': 'Authorization',
            'severity': 'High',
            'resolution': 'Verify AD groups, check role mappings, clear RBAC cache.',
            'error_code': 'RBAC-007',
        },
    },
    {
        'id': 9,
        'title': 'Incident Data Sync Delay',
        'content': 'Guardian incident data synchronization from source systems may experience delays exceeding the 15-minute SLA. Common causes include: source system API rate limiting, network congestion during peak hours, or the sync worker queue backlog exceeding 1000 items. Troubleshooting: check the sync worker queue depth in the Guardian admin dashboard, review source system API response times, verify the sync schedule in cron configuration, and check for any failed sync jobs in the job history.',
        'metadata': {
            'category': 'Data Sync',
            'severity': 'Medium',
            'resolution': 'Check queue depth, review API response times, verify cron schedule.',
            'error_code': 'SYNC-004',
        },
    },
    {
        'id': 10,
        'title': 'Deployment Rollback Procedure',
        'content': 'To perform a rollback of a Guardian deployment: (1) Identify the previous stable release version from the release history, (2) Execute kubectl rollout undo deployment/guardian-app -n guardian to revert to the previous version, (3) Verify the rollback with kubectl rollout status, (4) Run the smoke test suite with pytest tests/smoke/ -v, (5) Update the deployment tracker in Jira. For database migrations that need reversal, use python manage.py migrate chat <previous_migration_number> to reverse the schema changes.',
        'metadata': {
            'category': 'Deployment',
            'severity': 'High',
            'resolution': 'kubectl rollout undo, verify status, run smoke tests.',
            'error_code': 'DEPLOY-002',
        },
    },
    {
        'id': 11,
        'title': 'SSL Handshake Failure with Upstream Services',
        'content': 'SSL handshake failures with upstream services typically occur when the upstream service updates its TLS configuration or when there is a certificate chain issue. Debug with: openssl s_client -connect upstream-host:443 -showcerts. Common fixes: update the CA bundle in the Guardian trust store, verify that the intermediate certificates are included in the chain, and check that TLS 1.2 or higher is configured. Update the trust store path in guardian-ssl-config.yaml.',
        'metadata': {
            'category': 'Networking',
            'severity': 'High',
            'resolution': 'Update CA bundle, verify cert chain, ensure TLS 1.2+.',
            'error_code': 'NET-008',
        },
    },
    {
        'id': 12,
        'title': 'Kubernetes Pod CrashLoopBackOff',
        'content': 'CrashLoopBackOff in Guardian pods indicates the container is repeatedly crashing. Most common causes: (1) Application startup failure due to missing configuration, (2) Database migration not applied, (3) Insufficient memory allocation, (4) Health check probe configured incorrectly. Debug steps: kubectl describe pod <pod-name> to see events, kubectl logs <pod-name> --previous to see crash logs, verify ConfigMaps and Secrets are mounted correctly, and check if init containers completed successfully.',
        'metadata': {
            'category': 'Infrastructure',
            'severity': 'Critical',
            'resolution': 'Check pod events, review crash logs, verify ConfigMaps/Secrets.',
            'error_code': 'K8S-001',
        },
    },
]
