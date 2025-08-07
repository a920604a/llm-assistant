---
title: 'Chapter 1: Big Data'
tags: [system design]

---

Chapter 1: Big Data

[toc]

[:house:目錄](/8G7wHhrjTwqilLbCvByazQ) 
[:link: Reference link](https://www.oreilly.com/library/view/deciphering-data-architectures/9781098150754/ch01.html)

---
To do that, you need a data architecture to ingest, store, transform, andmodel the data (big data processing) so it can be accurately and easily used. 


## What Is Big Data, and How Can It Help You?

![](https://www.oreilly.com/api/v2/epubs/9781098150754/files/assets/deda_0101.png)

- volume
- variety
    - structured data(relational database)
    - semi-structured data(csv, xml, json format)
    - unstructured data(email, documents, pdfs)
    - binary data(image, audio, video)
- velocity
    - batch processing
    - real time
- vercacity
- Variability
- value


## Data Maturity
You may have heard many in the IT industry use the term **digital transformation** ,which refers to how companies embed technologies across their business to drivefundamental change in the way they get value out of data and in how they operateand deliver value to customers. 

### Stage 1: Reactive
In, the first stage, a company has data scattered all over.


Data architects call this a spreadmart (short for “spreadsheet data mart”): an informal, decentralized collection of data often found within an organization that uses spreadsheets to store, manage, and analyze data

### Stage 2: Informative
Companies reach the second maturity stage when they start to centralize their data,making analysis and reporting much easier. 

At stage 2, the solution built to **gather the data is usually not very scalable**. Generally,the size and types of data it can handle are limited, and it can ingest data only infrequently (every night, for example). Most companies are at stage 2, especially if theirinfrastructure is still on-prem (本地部署)


### Stage 3: Predictive

By stage 3, companies have **moved to the cloud** and have built a system that can **handle larger quantities of data**, different types of data, and data that is ingested more fre‐quently (hourly or streaming). 

### Stage 4: Transformative
Finally, at stage 4, the company has built a solution that can handle any data, no mat‐ter its size, speed, or type. It is easy to onboard new data with a shortened lead timebecause the architecture can handle it and has the infrastructure capacity to supportit. 


## Self-Service Business Intelligence
- traditional BI
For many years, if an end user within an organization needed a report or dashboard,they had to gather all their requirements (the source data needed, plus a descriptionof what the report or dashboard should look like), fill out an IT request form, andwait. IT then built the report, which involved extracting the data, loading it into thedata warehouse, building a data model, and then finally creating the report or dash‐board. This process is now called “traditional BI” .

- self-service BI
The goal of any data architecture solution you build should be to make it quick andeasy for any end user, no matter what their technical skills are, to query the data andto create reports and dashboards. They should not have to get IT involved to performany of those tasks—they should be able to do it all on their own
