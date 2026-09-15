# Beginner AWS Console Guide: S3 + CloudFront

This tutorial starts from zero. It explains every important click in simple words.

## What we are making

We will upload a small website to a **private Amazon S3 bucket**. Visitors will open the website through **Amazon CloudFront**.

```text
Visitor → CloudFront → Private S3 bucket
```

- **S3** stores `index.html`, `styles.css`, `script.js`, and `error.html`.
- **CloudFront** gives us an HTTPS website address and delivers the files.
- **Origin Access Control (OAC)** allows CloudFront to read the private S3 files.

## Before you start

You need:

1. An AWS account.
2. Permission to use Amazon S3 and CloudFront.
3. The extracted project folder on your laptop.
4. A billing alert or AWS Budget configured.

> Important: S3 and CloudFront can create charges. Delete the lab resources after practice. Do not upload passwords, AWS keys, CNIC images, or other private files.

---

# Part 1 — Check the website on your laptop

## Step 1: Extract the ZIP file

1. Find `serverless-web-serving-s3-cloudfront.zip` on your laptop.
2. Right-click the ZIP file.
3. Click **Extract All**.
4. Click **Extract**.
5. Open the extracted `serverless-web-serving-s3-cloudfront` folder.

## Step 2: Open the website folder

1. Open the `website` folder.
2. Confirm that these four files are present:
   - `index.html`
   - `styles.css`
   - `script.js`
   - `error.html`

## Step 3: Test the design locally

1. Double-click `index.html`.
2. It should open in Chrome or another browser.
3. Confirm that you can see the dark AWS-themed design and colors.
4. Keep the `website` folder ready. We will upload its contents to S3.

---

# Part 2 — Sign in and select a Region

## Step 4: Open the AWS Console

1. Open `https://console.aws.amazon.com/` in your browser.
2. Sign in to your AWS account.
3. You will see the **AWS Management Console** home page.

## Step 5: Select a Region

1. Look at the top-right area of the AWS Console.
2. Click the currently selected Region name.
3. Select a Region close to you. For this lab, you can select **Asia Pacific (Mumbai) — ap-south-1**.
4. Remember this Region. The S3 bucket will be created there.

> CloudFront is a global service, so its console does not work like a normal regional service. Your S3 bucket still belongs to the Region selected during bucket creation.

---

# Part 3 — Create a private S3 bucket

## Step 6: Open Amazon S3

1. Click the search bar at the top of the AWS Console.
2. Type `S3`.
3. Under **Services**, click **S3**.
4. The Amazon S3 page will open.

## Step 7: Start creating the bucket

1. In the left menu, click **General purpose buckets**. In some console views this may appear as **Buckets**.
2. Click the orange **Create bucket** button.

## Step 8: Enter the bucket name and Region

1. Under **General configuration**, find **Bucket name**.
2. Enter a globally unique name, for example:

   `luqman-serverless-web-2026-unique123`

3. Use only lowercase letters, numbers, and hyphens.
4. Do not copy the example exactly. Add your own numbers because every S3 bucket name must be unique.
5. Under **AWS Region**, select the same Region chosen earlier, for example **ap-south-1**.

## Step 9: Keep Object Ownership secure

1. Find **Object Ownership**.
2. Select or keep **ACLs disabled (recommended)**.
3. Confirm that **Bucket owner enforced** is selected.

## Step 10: Keep the bucket private

1. Find **Block Public Access settings for this bucket**.
2. Keep **Block all public access** checked.
3. Do not remove any of the four public-access checks.

This is correct. We do not need a public bucket because CloudFront will use OAC.

## Step 11: Enable versioning

1. Find **Bucket Versioning**.
2. Select **Enable**.

Versioning keeps older versions when a website file is replaced. It is useful for recovery, but old versions also use storage.

## Step 12: Choose encryption

1. Find **Default encryption**.
2. Choose **Server-side encryption with Amazon S3 managed keys (SSE-S3)**.
3. Do not create a KMS key for this beginner project.

## Step 13: Create the bucket

1. Leave the remaining settings at their defaults.
2. Scroll to the bottom.
3. Click **Create bucket**.
4. Wait for the green success message.
5. Find your new bucket in the bucket list.

> Do not enable **Static website hosting** in S3 Properties. This project uses the private S3 REST origin with CloudFront OAC, not the public S3 website endpoint.

---

# Part 4 — Upload the website files

## Step 14: Open the new bucket

1. In the S3 bucket list, click your bucket name.
2. The **Objects** tab should open.
3. Click **Upload**.

## Step 15: Add the files

1. Open the extracted project folder on your laptop.
2. Open the `website` folder.
3. In the S3 Upload page, click **Add files**.
4. Select these files:
   - `index.html`
   - `styles.css`
   - `script.js`
   - `error.html`
5. Click **Open**.

Do not upload the outer `website` folder as one extra folder. The files should appear at the root of the bucket. You should see `index.html`, not `website/index.html`.

## Step 16: Upload the files

1. Check that all four files appear in the upload list.
2. Leave the remaining upload settings at their defaults.
3. Scroll down.
4. Click **Upload**.
5. Wait until the status says the upload succeeded.
6. Click **Close**.

## Step 17: Confirm the S3 files

1. On the bucket **Objects** tab, confirm that all four files are visible.
2. Do not click **Make public**.
3. It is normal if a direct S3 object link returns **Access Denied**. The bucket is private.

---

# Part 5 — Create the CloudFront distribution

## Step 18: Open CloudFront

1. Click the AWS search bar at the top.
2. Type `CloudFront`.
3. Under **Services**, click **CloudFront**.
4. The Amazon CloudFront page will open.

## Step 19: Start a distribution

1. In the left menu, click **Distributions** if it is not already selected.
2. Click **Create distribution**.
3. In **Distribution name**, enter:

   `serverless-web-serving-s3-cloudfront`

4. Select **Single website or app**.
5. Click **Next**.
6. If AWS shows another introductory page, click **Next** again.

## Step 20: Select Amazon S3 as the origin

1. On the **Origin type** page, select **Amazon S3**.
2. Find **S3 origin**.
3. Click **Browse S3**.
4. Select the private bucket created earlier.
5. Confirm that the selected origin is the normal S3 bucket endpoint, not an S3 website endpoint.

## Step 21: Enable private access with OAC

1. Under **Settings**, select **Use recommended origin settings**.
2. The recommended S3 settings create or use **Origin Access Control (OAC)**.
3. If the console shows a signing option, select **Sign requests (recommended)**.
4. Do not select a legacy **Origin Access Identity (OAI)**.
5. Do not choose **Do not sign requests** because that requires a public S3 origin.
6. Click **Next**.

## Step 22: Choose WAF for this lab

1. AWS may show an **Enable security protections** page.
2. For a small learning lab, choose the option that does **not** enable AWS WAF.
3. Read the pricing information shown by AWS before enabling any paid protection.
4. Click **Next**.

## Step 23: Create the distribution

1. Review the settings.
2. Confirm that the origin is your S3 bucket.
3. Confirm that recommended S3 origin settings or OAC are enabled.
4. Click **Create distribution**.
5. CloudFront will update the S3 bucket policy for the new distribution.
6. Wait until deployment finishes. The page may show **Deploying** for several minutes.
7. Copy the CloudFront domain name. It looks similar to:

   `d123example.cloudfront.net`

---

# Part 6 — Set index.html as the home page

## Step 24: Edit the distribution settings

1. In CloudFront, open **Distributions**.
2. Click the distribution name.
3. Open the **General** tab.
4. In the **Settings** section, click **Edit**.
5. Find **Default root object**.
6. Enter exactly:

   `index.html`

7. Do not enter `/index.html`. There must be no slash at the start.
8. Scroll down and click **Save changes**.
9. Wait for the new distribution change to finish deploying.

---

# Part 7 — Open and test the website

## Step 25: Open the CloudFront URL

1. Return to the distribution **General** page.
2. Copy the **Distribution domain name**.
3. Add `https://` before it, for example:

   `https://d123example.cloudfront.net`

4. Paste it into a new browser tab.
5. Press Enter.
6. The colored website should open.

## Step 26: Confirm the security

1. Return to Amazon S3.
2. Open your bucket.
3. Open the **Permissions** tab.
4. Confirm that **Block public access** says **On**.
5. Under **Bucket policy**, you should see a policy that allows the CloudFront service to read objects for this distribution.
6. Return to CloudFront.
7. Open your distribution.
8. Open the **Origins** tab.
9. Select the S3 origin and click **Edit** only if you want to inspect it.
10. Confirm that Origin Access Control is attached. Click **Cancel** if you did not change anything.

The correct result is:

- CloudFront URL: website opens.
- Direct S3 object URL: Access Denied.

---

# Part 8 — Update the website later

## Step 27: Replace a website file

1. Edit `index.html` or `styles.css` on your laptop.
2. Open Amazon S3.
3. Open the same bucket.
4. Click **Upload**.
5. Click **Add files**.
6. Select the changed file.
7. Click **Upload**.
8. S3 creates a new version because versioning is enabled.

## Step 28: Clear the CloudFront cache

1. Open CloudFront.
2. Open your distribution.
3. Open the **Invalidations** tab.
4. Click **Create invalidation**.
5. In **Object paths**, enter:

   `/*`

6. Click **Create invalidation**.
7. Wait until the invalidation status is complete.
8. Refresh the CloudFront website URL.

> Invalidations can have pricing implications. For frequently updated production websites, versioned file names are often better.

---

# Part 9 — Common problems

## Problem: The page shows Access Denied

Check these items:

1. The CloudFront distribution has finished deploying.
2. `index.html` exists at the root of the S3 bucket.
3. Default root object is `index.html`, not `/index.html`.
4. OAC is attached to the S3 origin.
5. The S3 bucket policy contains permission for the correct CloudFront distribution.
6. You are opening the CloudFront URL, not the S3 URL.

## Problem: The page opens but has no colors

1. Confirm that `styles.css` was uploaded at the bucket root.
2. Confirm that the file name is exactly `styles.css` with lowercase letters.
3. Create a CloudFront invalidation for `/*`.
4. Refresh the page with `Ctrl + F5`.

## Problem: The newest changes are not visible

CloudFront may still have the older file in its cache. Create an invalidation for `/*`, wait for it to finish, and refresh the page.

---

# Part 10 — Delete the lab and stop future charges

Deleting resources is permanent. Download anything you want to keep before continuing.

## Step 29: Disable CloudFront

1. Open CloudFront.
2. Open **Distributions**.
3. If the distribution still says **Deploying**, wait for it to finish.
4. Select the checkbox beside your distribution.
5. Click **Disable**.
6. Confirm by clicking **Yes, Disable**.
7. Close the confirmation window.
8. Wait until a new timestamp appears under **Last modified**.

## Step 30: Delete CloudFront

1. Select the disabled distribution again.
2. Click **Delete**.
3. Confirm **Delete**.
4. If the Delete button is unavailable, wait a few minutes and try again after the Last modified time changes.

## Step 31: Empty the S3 bucket

1. Open Amazon S3.
2. Open **General purpose buckets** or **Buckets**.
3. Select the option beside your project bucket.
4. Click **Empty**.
5. On the confirmation page, type the complete bucket name.
6. Click **Empty**.
7. Wait for the empty operation to finish.

This removes current objects, old versions, and delete markers. It cannot be undone.

## Step 32: Delete the S3 bucket

1. Return to the bucket list.
2. Select the option beside the empty project bucket.
3. Click **Delete**.
4. Type the complete bucket name.
5. Click **Delete bucket**.
6. Search for the bucket name again. If it is not found, deletion succeeded.

---

# Final checklist

Before calling the project complete, confirm:

- [ ] The four website files are in the S3 bucket root.
- [ ] S3 Block Public Access is on.
- [ ] S3 static website hosting is not enabled.
- [ ] CloudFront uses the private S3 bucket as its origin.
- [ ] CloudFront OAC is enabled with signed requests.
- [ ] Default root object is `index.html`.
- [ ] The website opens through the CloudFront HTTPS address.
- [ ] The direct S3 object address does not open publicly.
- [ ] Lab resources are deleted after practice if they are no longer needed.

## Official AWS references

- [Create an S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)
- [Upload files to S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html)
- [Create a CloudFront distribution with an S3 origin and OAC](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.SimpleDistribution.html)
- [Restrict access to an S3 origin](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [Set the default root object](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DefaultRootObject.html)
- [Invalidate CloudFront files](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html)
- [Delete a CloudFront distribution](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/HowToDeleteDistribution.html)
- [Empty an S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/empty-bucket.html)

