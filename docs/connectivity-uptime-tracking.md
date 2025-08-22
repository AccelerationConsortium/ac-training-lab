# Internet Connectivity and Uptime Tracking Across AC Training Lab

This document provides comprehensive information about network infrastructure, contacts, and best practices for tracking internet connectivity and uptime across the Acceleration Consortium (AC) Training Lab facilities and partners.

## Network Infrastructure Overview

The AC Training Lab operates across multiple facilities with diverse network requirements:

- **University of Toronto (UofT)** - Primary campus infrastructure with WPA2-Enterprise
- **Donnelly Centre (SDL6)** - Self-Driving Laboratory 6 with automated systems
- **Structural Genomics Consortium (SDL3)** - Self-Driving Laboratory 3 for protein research
- **Hologram IoT** - Cellular/SIM card backup connectivity
- **Rogers Mobile Hotspot** - Canadian mobile backup solutions

## Facility-Specific Information

### University of Toronto (UofT)

**Network Setup:**
- **WiFi Security:** WPA2-Enterprise with UofT credentials
- **Infrastructure:** Campus-wide secure wireless networks
- **Coverage:** Multiple buildings and research facilities

**Key Contacts:**
- **Central IT Help Desk:** help.desk@utoronto.ca | 416-978-HELP (4357)
- **Engineering Faculty IT:** helpdesk@ecf.utoronto.ca | 416-946-5663
- **Arts & Science IIT:** iit@artsci.utoronto.ca | 416-946-0570
- **Computer Science IT:** pocai@cs.toronto.edu | 416-946-8487

**For Research Collaboration:**
Contact Central IT Help Desk with formal inquiry specifying "network monitoring and reliability research" for proper routing to network administrators.

### Donnelly Centre (SDL6)

**Network Infrastructure:**
- **Architecture:** Robust network with internet and secure internal networks
- **Access:** University of Toronto WiFi and VPN for off-site access
- **Segmentation:** Network closets on each floor with switches and firewalls
- **HPC Resources:** Internal high-performance computing systems
- **Cloud Integration:** AWS Cloud Research Lab for scalable computing

**Key Contacts:**
- **Systems Administrator:** Jeff Liu - jeffs.liu@utoronto.ca
- **General IT Support:** support@rt.ccbr.utoronto.ca
- **Enterprise Networking:** en.help@utoronto.ca

**Automated Systems:**
- High-throughput DNA sequencers and imaging systems
- Requires high-bandwidth network segments for rapid data transfer
- Flexible infrastructure supporting both wet labs and data-intensive applications

### Structural Genomics Consortium (SDL3)

**Network Infrastructure:**
- **Global Distribution:** Multi-site operation with University of Toronto as major hub
- **Data Platform:** Open, cloud-accessible platforms for large-scale biological datasets
- **Requirements:** High-speed scientific networking, secure remote access, robust storage

**Key Contacts:**
- **General Inquiries:** info@thesgc.org
- **CSO Toronto:** Dr. Cheryl Arrowsmith (institutional matters)

**Automated Systems:**
- Robotic sample handling and automated screening systems
- Affinity selection mass spectrometry (AS-MS)
- DNA-encoded chemical library (DEL) assays
- Machine-learning-driven data analysis pipelines

**Network Requirements:**
- Uninterrupted local network connectivity to robotic instruments
- Integration with HPC clusters for AI/ML workflows
- Secure VPN/remote access for collaborative open science

### Hologram IoT (Cellular Backup)

**Service Overview:**
- **Global Coverage:** 550+ networks in 190+ countries
- **Technologies:** 2G, 3G, 4G, 5G, LTE-M, NB-IoT
- **Redundancy:** Automatic network switching for optimal connectivity

**Key Features:**
- **eUICC Hyper SIM Cards:** Remotely reprogrammable for network selection
- **Performance:** Up to 300Mbps speeds, ~50ms latency
- **Reliability:** Outage-proof solution with guaranteed uptime claims
- **Multi-carrier failover:** Automatic switching to best available network

**Contact Information:**
- **Enterprise Sales:** Contact form on hologram.io website
- **Technical Support:** Support portal via dashboard
- **Pricing:** Starting at $0.03/MB + $1/month/SIM

**Backup Connectivity Use:**
- Ideal for router failover when primary connectivity fails
- Automatic switching to cellular when wired/wireless service drops
- Remote monitoring and control via management dashboard

### Rogers Mobile Hotspot (Canadian Backup)

**Network Infrastructure:**
- **Coverage:** Extensive nationwide LTE and 5G deployment
- **Technology:** Ericsson 5G Advanced with network slicing
- **Reliability:** Separated IP cores for wireless/wireline resilience

**Key Contacts:**
- **Business Support:** 1-888-ROGERS-1 (1-888-764-3771)
- **Online:** Rogers Business website contact forms and live chat
- **Enterprise:** Dedicated account managers for large organizations

**Backup Connectivity:**
- Portable Wi-Fi/5G hotspot routers with cellular connectivity
- Multiple device support for immediate backup internet
- High-availability solution for critical business functions

## Best Practices for Connectivity and Uptime Monitoring

### Industry Standard Tools

**Comprehensive Monitoring Platforms:**
- **SolarWinds Network Performance Monitor**
- **Paessler PRTG Network Monitor**
- **ManageEngine OpManager**
- **Zabbix** (open source)

**Key Features:**
- Real-time monitoring and automated device discovery
- Customizable dashboards and alerting systems
- Root-cause analysis and third-party integration
- SNMP and agent-based monitoring capabilities

### Laboratory Environment Best Practices

**Network Segmentation:**
- Isolate critical automated lab units
- Implement target-specific monitoring and dashboards
- Contain issues to prevent cascade failures

**Proactive Monitoring:**
- Real-time monitoring of network and attached devices
- Automated alerts and escalation workflows
- Immediate notification of anomalies or outages

**Documentation and Mapping:**
- Automated device discovery and inventory maintenance
- Updated network documentation for troubleshooting
- Regular configuration reviews and updates

### Key Metrics and KPIs

**Primary Reliability Metrics:**
- **Uptime (%):** Proportion of time network is available
- **Mean Time Between Failures (MTBF):** Average time between failures
- **Mean Time to Repair (MTTR):** Average restoration time
- **Packet Loss (%):** Frequency of dropped packets

**Performance Metrics:**
- **Latency (ms):** Data traversal time across network
- **Jitter:** Variation in latency (critical for real-time data)
- **Link Utilization (%):** Bandwidth usage for capacity planning
- **Number of Incidents:** Monthly/quarterly stability trends

## Fault Tolerance in Industrial Automation

### Common Failover Strategies

**Redundancy:**
- Duplicate critical components (controllers, sensors, networks)
- No single point of failure for essential operations
- Automatic switchover to backup systems

**Local Fallback Modes:**
- Programmable Logic Controllers (PLCs) for autonomous control
- Local operation when cloud coordination is unreachable
- Graceful degradation to essential safety processes

**Continued Operation:**
- Reasonable time operation under controlled conditions
- Risk management and safety maintenance during outages
- Alert operators to connectivity loss

### Edge Computing vs Cloud-Dependent Systems

| Aspect | Edge Computing | Cloud-Dependent |
|--------|----------------|-----------------|
| **Connectivity Requirements** | Works offline, processes locally | Requires stable internet |
| **Fault Tolerance** | High autonomy, resilient to outages | May halt during connectivity loss |
| **Latency** | Minimal local decisions | Can be high with poor connections |
| **Examples** | PLCs, local servers, on-prem AI | Cloud SCADA, remote monitoring |

### Local Backup and Offline Operation

**Local Backup Controllers:**
- Continuous synchronization with cloud systems
- Instant takeover when cloud links break
- Stored operating parameters and logic for safe operation

**Offline Capabilities:**
- Maintain safe operations until reconnection
- Safety protocols return to safe-mode automatically
- Local data acquisition and logging continue

### Monitoring vs Decision-Making During Outages

**Monitoring Capabilities:**
- Local data acquisition continues during outages
- Remote monitoring and analytics unavailable
- Local alarms and basic alerting remain functional

**Decision-Making:**
- Local controllers execute automated control logic
- Process stability and safety functions maintained
- External/aggregate data decisions paused until reconnection
- Safety-critical functions remain local and autonomous

## Cloud vs Local System Reliability

### Reliability Comparison

**Cloud Systems Advantages:**
- Global redundant infrastructure with automated failover
- Continuous monitoring and maintenance by dedicated providers
- Frequent security updates and patches
- Geographic disaster recovery capabilities

**On-Premises Advantages:**
- Full control over data and security policies
- Customizable security implementations
- Regulatory compliance control
- Lower latency for local applications

### Uptime Statistics and SLAs

**Cloud Provider SLAs:**
- **99.9% (three nines):** <8.76 hours downtime/year
- **99.99% (four nines):** <1 hour downtime/year
- Predictable uptime with financial penalties for breaches

**On-Premises Reliability:**
- Depends heavily on organizational investment
- No formalized SLAs unless internally established
- Variable uptime based on infrastructure quality

### Hybrid Approach Best Practices

**Maximum Reliability Strategy:**
- **Geographic Redundancy:** Replicate across cloud regions and local sites
- **Real-time Failover:** Automatic switching between cloud and on-premises
- **Regular Backup Testing:** Scheduled disaster recovery validation
- **Compliance Alignment:** Balance operational goals with regulatory requirements

**Implementation Recommendations:**
- Use cloud for scalability and disaster recovery
- Keep sensitive data local for security and compliance
- Implement automated failover between systems
- Regular testing of all redundancy mechanisms

## Implementation Recommendations for AC Training Lab

### Immediate Actions

1. **Establish Primary Contacts:**
   - Reach out to UofT Central IT for research collaboration discussion
   - Contact Donnelly Centre Systems Administrator for SDL6 coordination
   - Initiate dialogue with SGC for SDL3 monitoring cooperation

2. **Evaluate Backup Connectivity:**
   - Assess Hologram IoT for critical device backup connectivity
   - Consider Rogers mobile hotspots for facility-level backup
   - Test failover mechanisms in controlled environment

3. **Implement Monitoring Infrastructure:**
   - Deploy comprehensive network monitoring tools (recommend starting with Zabbix for cost-effectiveness)
   - Establish baseline metrics and KPIs for all facilities
   - Set up automated alerting and escalation procedures

### Long-term Strategy

1. **Hybrid Architecture Development:**
   - Design edge computing capabilities for critical lab functions
   - Implement cloud integration for data analysis and collaboration
   - Establish redundant connectivity paths

2. **Collaborative Monitoring:**
   - Work with facility administrators to share uptime data
   - Develop joint monitoring dashboards and reporting
   - Establish incident response coordination procedures

3. **Continuous Improvement:**
   - Regular review of monitoring effectiveness
   - Update failover procedures based on lessons learned
   - Expand monitoring to new facilities and devices as lab grows

## Conclusion

Effective connectivity and uptime tracking across the AC Training Lab requires a multi-faceted approach combining robust monitoring tools, redundant connectivity solutions, and collaborative relationships with facility administrators. The hybrid architecture model, leveraging both cloud and local capabilities, provides the optimal balance of reliability, performance, and control for the diverse requirements of automated laboratory environments.

Regular testing, monitoring, and improvement of these systems will ensure the AC Training Lab maintains high availability and reliability as it continues to expand and evolve.