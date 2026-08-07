Submit one document or form response containing:
# Your Databricks App URL
https://ticketing-7474651165193831.aws.databricksapps.com


# Your source code zipped up
https://github.com/zen37/databricks-lakebase-ticketing/


# A screenshot of the deployed application
<img width="1493" height="701" alt="image" src="https://github.com/user-attachments/assets/1c683da0-6efc-4bbe-adb9-d744d3257102" />


# A screenshot showing the Lakebase tables and sample records

<img width="1491" height="443" alt="image" src="https://github.com/user-attachments/assets/5063fec5-bc9b-4a47-aa40-22d5ac66a0b8" />

<img width="1481" height="459" alt="image" src="https://github.com/user-attachments/assets/1cb317a2-b2b1-4638-99e9-e9907d7974f1" />


# A short reflection of 3–5 sentences answering:

## What was the most difficult part?
* security hardening (still not done)
* the database design, the two required tables quickly felt too thin, and I kept wanting extra tables and fields (like a resolved_at column or a status-history table) to build a more comprehensive solution

## How is Lakebase different from storing this data in a traditional analytics table?

Lakebase CDF captures changes happening IN Lakebase (your operational database) and persists them to Unity Catalog Delta tables for analytics.


## What feature would you add next?

see file features.next.md
