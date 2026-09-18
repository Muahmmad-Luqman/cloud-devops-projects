# Beginner AWS Console Guide

## AWS VPC, Application Load Balancer and Auto Scaling

Author: Muhammad Luqman. Research date: 18 September 2026.

This is a reproducible reference walkthrough, not a claim that every setting matches the original lab. Names, CIDRs, operating system and warmup values below are chosen examples. The supplied VPC creation preview showed two public and two private subnets across us-east-1a and us-east-1b, but did not show a NAT Gateway. This guide explicitly adds one later.

Console labels and available AZs vary. If a screen differs, match the meaning of the setting rather than clicking an unrelated option. Stop on permission or billing restrictions; do not bypass them.

## Part 1 — Prepare Your Account

### Step 1: Sign in

1. Open your browser.
2. Open https://console.aws.amazon.com/.
3. Sign in using your authorized AWS identity; prefer an IAM/Identity Center identity rather than root for routine work.
4. Never share passwords, access keys or MFA codes.

### Step 2: Check costs before creating resources

1. Search for `Billing` in the console search bar.
2. Open Billing and Cost Management.
3. Check your account's credits and applicable plan. Do not assume this lab is free.
4. Open Budgets and configure a cost budget with notifications if your permissions allow it.
5. Review current pricing for NAT Gateway, public IPv4, ALB, EC2, EBS and CloudWatch detailed monitoring.
6. Understand that budget notifications do not automatically stop spending.

### Step 3: Select the Region

1. Open the Region menu in the console's top-right area.
2. Select US East (N. Virginia), `us-east-1`, for this example.
3. Keep all regional project resources in this Region.
4. Record your resource names in a private lab notebook to distinguish them from unrelated resources.

## Part 2 — Create the VPC and Subnets

### Step 4: Open the VPC creation screen

1. Click the console search bar.
2. Type `VPC`.
3. Open VPC under Services.
4. Click Create VPC.
5. Select VPC and more.
6. Enable Name tag auto-generation and enter `project`.

### Step 5: Enter the network settings

1. Enter `10.0.0.0/16` for IPv4 CIDR.
2. Select No IPv6 CIDR block.
3. Keep Tenancy as Default.
4. Select 2 Availability Zones.
5. Expand Customize AZs and choose two different available AZs, such as us-east-1a and us-east-1b.
6. Select 2 public subnets and 2 private subnets.
7. Expand Customize subnet CIDR blocks.
8. Assign the following non-overlapping CIDRs, matching each subnet to its AZ:

| Subnet | AZ | CIDR |
|---|---|---|
| Public A | A | 10.0.1.0/24 |
| Public B | B | 10.0.2.0/24 |
| Private A | A | 10.0.11.0/24 |
| Private B | B | 10.0.12.0/24 |

### Step 6: Review and create networking

1. Select None under NAT gateways. We will add a zonal NAT Gateway separately for an explicit beginner workflow.
2. Select S3 Gateway under VPC endpoints if shown. This endpoint is not a substitute for general internet or Systems Manager connectivity.
3. Enable DNS resolution and DNS hostnames for this reference design.
4. Review the preview: one VPC, four subnets, a public route table, private route tables and an Internet Gateway.
5. Click Create VPC.
6. Wait for completion and open Your VPCs.
7. Select project-vpc and confirm State is Available.
8. Open its Resource map and capture your first evidence screenshot.

### Step 7: Verify the public route

1. Open Route tables in the VPC navigation menu.
2. Select the project public route table.
3. Open Routes.
4. Confirm a local VPC route exists.
5. Confirm destination `0.0.0.0/0` targets the project's Internet Gateway.
6. Open Subnet associations and confirm both public subnets are explicitly associated.
7. If a route is absent, click Edit routes, Add route, enter `0.0.0.0/0`, choose Internet Gateway, select the project's gateway, and Save changes.

## Part 3 — Add the NAT Gateway

### Step 8: Create one zonal public NAT Gateway

1. In VPC, open NAT gateways.
2. Click Create NAT gateway.
3. Enter `project-nat-a` for its name.
4. If a choice is shown, select the Zonal deployment type. This walkthrough does not configure a Regional NAT Gateway.
5. Choose Public A as the subnet.
6. Choose Public connectivity.
7. Click Allocate Elastic IP, or choose an unused Elastic IP allocated specifically for this lab.
8. Review pricing and click Create NAT gateway.
9. Wait for the NAT Gateway state to become Available.

One zonal NAT is a lab tradeoff: AZ B's outbound traffic depends on AZ A and can incur cross-AZ transfer charges. This is not the resilient production NAT topology.

### Step 9: Add private default routes

1. Open Route tables.
2. Select the private route table associated with Private A.
3. Open Routes and click Edit routes.
4. Click Add route.
5. Enter `0.0.0.0/0` as the destination.
6. Choose NAT Gateway as the target type and select project-nat-a.
7. Click Save changes.
8. Repeat these actions for Private B's route table.
9. Confirm each private route table is associated with its intended private subnet.
10. Keep the local route and any S3 endpoint route. Do not replace them.
11. Never point a private subnet's default route directly to the Internet Gateway in this design.

## Part 4 — Configure Security Groups

### Step 10: Create the Load Balancer security group

1. Search for EC2 and open the EC2 console.
2. Open Security Groups under Network & Security.
3. Click Create security group.
4. Enter `project-alb-sg` and a description such as `Public HTTP demo access`.
5. Select project-vpc, not the default VPC.
6. Under Inbound rules, click Add rule.
7. Select HTTP, TCP port 80, and source `0.0.0.0/0`.
8. Under Outbound rules, replace unrestricted egress with HTTP, TCP port 80, destination `10.0.0.0/16` for this lab.
9. Click Create security group.

HTTP is for a non-sensitive demo only. Production requires an HTTPS listener with an ACM certificate; do not send passwords or private information through this HTTP demo.

### Step 11: Create the web-server security group

1. Click Create security group again.
2. Enter `project-web-sg` and select project-vpc.
3. Add an inbound HTTP rule on TCP port 80.
4. Choose a security group as the source and select project-alb-sg.
5. Do not use `0.0.0.0/0` as the web-server inbound source.
6. Do not add an SSH rule; administration will use Session Manager.
7. Keep default outbound access for bootstrap downloads and Systems Manager. This is broader egress for a learning lab, not strict production least privilege.
8. Click Create security group.

## Part 5 — Prepare Session Manager Access

### Step 12: Create an EC2 role

1. Search for IAM and open it.
2. Open Roles and click Create role.
3. Select AWS service as the trusted entity type.
4. Select EC2 as the service/use case and click Next.
5. Search for AmazonSSMManagedInstanceCore.
6. Select that policy and click Next.
7. Name the role `project-ec2-ssm-role`.
8. Review the EC2 trust relationship and click Create role.
9. Return to the EC2 console in us-east-1.

Your own sign-in identity also needs permission to start sessions. The instance role alone does not authorize your user. Instances need a running SSM Agent and outbound HTTPS connectivity to the applicable Systems Manager endpoints. The NAT Gateway provides that connectivity here.

## Part 6 — Create the Target Group and Load Balancer

### Step 13: Create the Target Group

1. In EC2, open Target Groups under Load Balancing.
2. Click Create target group.
3. Select Instances as the target type.
4. Name it `project-web-tg`.
5. Choose HTTP and port 80.
6. Choose project-vpc.
7. Keep the protocol version as HTTP1.
8. Set the health-check protocol to HTTP and path to `/`.
9. Keep success code 200.
10. Click Next.
11. Leave manual target registration empty; the ASG will register its instances.
12. Click Create target group.

### Step 14: Create the Application Load Balancer

1. Open Load Balancers and click Create load balancer.
2. Under Application Load Balancer, click Create.
3. Enter `project-alb` as the name.
4. Choose Internet-facing and IPv4.
5. Choose project-vpc.
6. Under Network mapping, select both AZs.
7. For each AZ, select its PUBLIC subnet. Do not choose the private subnets here.
8. Select project-alb-sg and remove any unintended default security group.
9. Set the listener to HTTP, port 80.
10. Set the default forward action to project-web-tg.
11. Do not enable optional paid integrations without reviewing their costs.
12. Review and click Create load balancer.
13. Wait for the state to become Active.
14. Record its DNS name. It may return 503 until healthy instances register.

## Part 7 — Create the Launch Template

### Step 15: Configure instance launch settings

1. Open Launch Templates under Instances.
2. Click Create launch template.
3. Name it `project-web-lt`.
4. Add a version description such as `Amazon Linux web server with Session Manager`.
5. Enable Auto Scaling guidance if offered.
6. Select Amazon Linux 2023, x86_64 architecture, from AWS's official AMIs.
7. Choose t3.micro for this example after checking eligibility and pricing.
8. Select Proceed without a key pair because this guide uses Session Manager.
9. Do not select a subnet in the template; subnet placement belongs to the ASG.
10. Select project-web-sg as the security group.
11. Keep public IP assignment disabled or inherited from the private subnets, which must have auto-assignment disabled.
12. Review the default EBS disk and ensure delete-on-termination is enabled for the lab root volume.

### Step 16: Configure advanced details

1. Expand Advanced details.
2. Select project-ec2-ssm-role as the IAM instance profile.
3. Enable detailed CloudWatch monitoring for one-minute CPU metrics. Charges may apply.
4. Require IMDSv2 under metadata settings.
5. Open `scripts/user-data.sh` from this package.
6. Copy its entire contents, including the first `#!/bin/bash` line.
7. Paste them into User data as plain text; do not pre-encode them unless your interface explicitly requires it.
8. Click Create launch template.

The bootstrap installs Apache and writes a demo page that includes the serving hostname. Every newly launched instance gets the same setup. Failed outbound routing can prevent package installation and leave the target unhealthy.

## Part 8 — Create the Auto Scaling Group

### Step 17: Select the template and private subnets

1. Open Auto Scaling Groups.
2. Click Create Auto Scaling group.
3. Name it `project-web-asg`.
4. Select project-web-lt and its intended version.
5. Click Next.
6. Use the instance type specified in the template.
7. Select project-vpc.
8. Select Private A and Private B as the instance subnets.
9. Continue to the integration settings.

### Step 18: Attach load balancing and health checks

1. Choose Attach to an existing load balancer.
2. Choose the existing load-balancer target group option.
3. Select project-web-tg.
4. Enable Elastic Load Balancing health checks in addition to EC2 health checks.
5. Set the health-check grace period to 300 seconds for this example.
6. Leave unrelated integrations disabled.
7. Click Next.

### Step 19: Configure capacity and scaling

1. Set Desired capacity to 1.
2. Set Minimum capacity to 1.
3. Set Maximum capacity to 4.
4. Choose a Target tracking scaling policy.
5. Name it `project-load-60`.
6. For the reproducible reference, select Average CPU utilization and target value 60.
7. Enable default instance warmup and enter 300 seconds if offered. Otherwise configure it after creation from the ASG's details.
8. Leave automatic scale-in enabled unless you intentionally need a temporary diagnostic exception.
9. Skip optional notifications for this small lab, or configure your own if desired.
10. Add tag Name = project-web and enable propagation to instances.
11. Review private subnet selection, target group, capacities and template version.
12. Click Create Auto Scaling group.

Simple explanation: sustained high VM load can cause extra VMs to launch. Precise behavior depends on GROUP AVERAGE, data availability, alarms, warmup and capacity limits. This is not an exact five-minute timer or an instruction to add exactly one VM. Do not edit the CloudWatch alarms managed by target tracking.

## Part 9 — Verify Initial Creation and Website Access

### Step 20: Check the automatically launched instance

1. Select project-web-asg.
2. Open Activity and wait for a successful instance launch event.
3. Open Instance management and record the instance ID.
4. Open EC2 Instances and confirm the instance is Running and its status checks pass.
5. Confirm it has a private address and no public IPv4 address.
6. Open project-web-tg and its Targets tab.
7. Wait for the instance to become Healthy. Bootstrap and health checks can take several minutes.
8. Capture the ASG capacities, Activity event and healthy target screenshots.

### Step 21: Open the website

1. Open project-alb's details.
2. Copy the DNS name.
3. Open `http://YOUR-ALB-DNS-NAME` in a new tab.
4. Confirm the demo page loads and record its serving hostname.
5. Capture a screenshot of the website without private account information.

Expected result: ASG launches one web server and ALB forwards requests to it. A minimum of one does not ensure uninterrupted service during replacement.

## Part 10 — Test Automatic Replacement

### Step 22: Terminate only the disposable lab instance

1. First confirm desired capacity is 1 and no stress test is running.
2. In EC2 Instances, select the exact project-web instance ID recorded above.
3. Confirm it belongs to this lab; do not select unrelated instances.
4. Choose Instance state, Terminate instance.
5. Read the permanent-deletion warning and confirm only if this disposable instance contains nothing you need.
6. Do not reduce the ASG's desired capacity.
7. Return to project-web-asg and open Activity.
8. Wait for a replacement launch event.
9. Record the NEW instance ID and compare it to the original.
10. Wait for it to become healthy in project-web-tg.
11. Refresh the ALB URL and capture evidence.

Expected result: the ASG restores desired capacity. This demonstrates self-healing, not load-driven scale-out. With one instance, the website can be temporarily unavailable during the test.

## Part 11 — Test Scale-Out With Bounded CPU Load

Run only on YOUR disposable lab instance. Do not run on production or someone else's infrastructure. The test generates LOCAL CPU load, not a network attack. It does not prove real customer-traffic performance or application load redistribution.

### Step 23: Connect using Session Manager

1. Select the replacement lab instance in EC2.
2. Click Connect.
3. Select Session Manager.
4. Click Connect to open the browser terminal.
5. If connection is unavailable, check the role, agent, private routes, NAT state and your user permissions. Do not add public SSH as a shortcut.
6. Run `curl -I http://localhost/` and check that the server responds.

### Step 24: Apply a short, automatically bounded load

1. Ensure no other load experiment is running on the instance.
2. Paste the following block into the Session Manager terminal:

```bash
test_pids=()
for ((i=0; i<$(nproc); i++)); do
  timeout 600s sh -c 'while :; do :; done' &
  test_pids+=("$!")
done
printf 'Started bounded CPU workers: %s\n' "${test_pids[*]}"
```

3. These workers use CPU for at most 10 minutes and then stop. Keep this terminal open.
4. Open another console tab, select the instance, open Monitoring and view CPU utilization.
5. Open the ASG's monitoring/scaling information and its target-tracking CloudWatch alarm.
6. Observe average CPU metrics and alarm changes. Do not modify the managed alarm.
7. Open Activity and look for a policy-triggered increase in desired capacity.
8. Check Instance management for additional instances.
9. Check project-web-tg for newly registered targets becoming healthy.
10. Capture the CPU chart, scaling event, capacities and healthy target list.
11. End the workers early, from the SAME terminal, as soon as sufficient evidence is collected:

```bash
for test_pid in "${test_pids[@]}"; do
  kill "$test_pid" 2>/dev/null || true
done
```

12. If the terminal was closed, the timeout still limits worker lifetime. Do not use broad process-kill commands against unrelated work.
13. Do not repeatedly restart the test just to chase a badge or exact instance count.

Expected result: sustained elevated average utilization may launch additional instances, up to four. After a second instance launches, load generated on only the first instance is not redistributed to the second, so group average may fall and further scaling may stop. Missing metrics, warmup, quotas, credit depletion or an insufficient evaluation period can prevent scale-out during a short test. That does not justify keeping paid resources under unlimited load.

### Step 25: Observe recovery after load ends

1. Confirm CPU utilization returns toward normal.
2. Watch the ASG Activity tab for optional scale-in.
3. Allow evaluation and warmup to finish; scale-in may be gradual.
4. Confirm capacity does not fall below one due to this policy.
5. Record an actual result rather than claiming scale-in happened if you did not observe it.

## Part 12 — Record Results Honestly

| Test | Evidence to collect | Your actual result |
|---|---|---|
| Initial launch | ASG Activity and first instance ID | Fill after running |
| Website | ALB URL and page screenshot | Fill after running |
| Automatic replacement | Old/new IDs and launch activity | Fill after running |
| Scale-out | CPU chart, policy event, new target | Fill after running |
| Scale-in, optional | Activity after load ends | Fill after running |
| Cleanup | Resource absence and billing review | Fill after running |

The original author reported observing initial launch, automatic replacement and one additional VM under load. Keep those original observations separate from new tests of this reference implementation.

## Part 13 — Troubleshoot

| Symptom | Checks |
|---|---|
| ALB returns 503 | Target group attached to ASG, instances registered, targets healthy |
| Target unhealthy | Web service running, `/` returns 200, correct port and SG source, user-data finished |
| Package install fails | Private default routes, NAT Available, public route to IGW, outbound rules |
| Session Manager unavailable | Agent running, instance profile, outbound HTTPS, user authorization |
| Replacement loop | Health-check grace period, bootstrap errors, target health reason |
| No scale-out | Average group metric, policy target, managed alarm, warmup, maximum four, EC2 quota |
| Page always shows same host | Check target count; ALB does not guarantee alternating hosts on every browser refresh |

In a Session Manager session, `sudo tail -n 100 /var/log/cloud-init-output.log` and `sudo systemctl status httpd` can help diagnose bootstrap errors. Never publish logs without checking for sensitive information.

## Part 14 — Clean Up and Verify

Deletion is permanent. Save anything needed and resolve exact project resources first. If you deployed with CloudFormation, DELETE THE STACK instead of manually dismantling its resources, then inspect residuals. For this manual console workflow:

### Step 26: Remove compute and load balancing

1. Stop any lab load workers or wait for their timeout.
2. Open Auto Scaling Groups and select ONLY project-web-asg.
3. Choose Delete and confirm the exact group name. Its managed instances will be terminated.
4. Wait until the group is gone and its EC2 instances are terminated.
5. Open Load Balancers, select project-alb, choose Delete and confirm.
6. Wait for the ALB and its managed network interfaces to disappear.
7. Open Target Groups and delete project-web-tg after it is no longer referenced.
8. Delete project-web-lt under Launch Templates if no other group uses it.

### Step 27: Remove NAT and network resources

1. In VPC, delete project-nat-a and wait for Deleted status.
2. In EC2 Elastic IPs, release ONLY the lab Elastic IP after NAT deletion and after confirming it is no longer associated.
3. Delete the project's S3 Gateway Endpoint.
4. Delete the custom project security groups after attached interfaces are removed.
5. Select project-vpc and choose Delete VPC.
6. Read the resource list carefully. Use the console's dependency report to remove remaining project-only subnets, custom route tables, or attached gateways if automatic deletion cannot complete.
7. Do not manually delete AWS-managed interfaces or unrelated shared resources.
8. Delete the project-specific IAM role/instance profile only when no instance or other resource uses it.

### Step 28: Check for leftovers

1. Check EC2 for running lab instances and unattached lab EBS volumes.
2. Check Load Balancers, NAT Gateways, Elastic IPs and VPC endpoints.
3. Check for any optional logs or alarms you created manually. Do not delete alarms belonging to other applications.
4. Check the Billing dashboard again after usage reporting updates. Deletion does not erase charges already incurred.
5. Record cleanup completion in the results table.

## Research References

See the README for AWS networking, scaling, launch-template and ALB sources. Additional references:

- [Create an ASG from a launch template](https://docs.aws.amazon.com/autoscaling/ec2/userguide/create-asg-launch-template.html)
- [Start a Session Manager session](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html)
- [Set Auto Scaling limits](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-capacity-limits.html)

The chosen names, CIDRs, sample website and bounded local CPU experiment are reference project content, not instructions copied verbatim from AWS. Always validate the template and permissions before deploying.
