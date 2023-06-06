<br/>
<p align="center">
  <img src="https://github.com/deep-ink-ventures/xrp-confirmify-poc/assets/120174523/c6256b39-ddc9-4db2-87d3-398ac4e45015">
  <i>A proof of authenticity protocol on the XRP Ledger</i>
</p>

<br /><br />

## Introduction
In our rapidly evolving digital age, the proliferation of artificial intelligence has inadvertently given rise to an increase in fabricated content. The problem is already visible now and will increase exponentially over the next months and years.

This manipulation has extended beyond mere text, with once reliable formats such as video becoming susceptible to counterfeiting. We face an impending future where the majority of disseminated text, audio, and video could be fraudulent. 
Public figures, corporations, governments, and media organizations are continuously grappling with an overwhelming influx of deceptive announcements and publications that contradict their official policies and principles.

<br />

## Our Solution: Confirmify

We propose a solution to this escalating problem - a publishing pipeline application designed to verify authenticity. The premise of our platform is to provide clients, such as businesses, with a streamlined dashboard for managing their media content. By publishing their content through our application, it automatically becomes authenticated and verifiable.

This innovation allows consumers, ranging from journalists to social media platforms, to confirm the authenticity of content they encounter. Whether it's a video trending on Twitter or an article shared on Facebook, our application ensures that the content is genuine and originated from a verified source.

<br/>
<p align="center">
  <img src="https://github.com/deep-ink-ventures/xrp-confirmify-poc/assets/120174523/adec9d07-2b2e-4497-be99-19c1d5c0c111">
</p><br />

At the heart of our platform is a novel application of blockchain technology, specifically Non-Fungible Tokens (NFTs). Each piece of published content is associated with an NFT, which references structured metadata that prominently includes a checksum of the published data. Through an easy-to-use API, consumers can instantly verify the authenticity of any content.

<br/>
<p align="center">
  <img src="https://github.com/deep-ink-ventures/xrp-confirmify-poc/assets/120174523/ddd0eccf-9152-407c-81b0-cd3420fd097b">
</p><br />

Although the underlying blockchain technology is complex, its application remains hidden under the hood of our platform. It serves as the backbone of our system, ensuring a tamper-proof protocol for verifying authenticity.

<br/>
<p align="center">
  <img src="https://github.com/deep-ink-ventures/xrp-confirmify-poc/assets/120174523/33834153-ac21-44a6-b357-b9a77cda2bfb">
</p><br />

Our application isn't just about verifying content; it's about restoring trust in the digital age, providing the tools necessary to separate fact from fiction in a world where artificial intelligence has blurred the line between reality and counterfeit.

<br />

## Why we choose Ripple
We are committed to the unix philosophy of doing one thing, but doing it right. Selecting the right tool for the right job.

Therefore, chain selection for us has a lot of components such as dev tooling, community and adoption; but one part is critical yet often overseen: Selecting the right chain to get the job done.

Ripple checkmarks on tooling, community and adoption. With the XLS-20d update, Ripple introduced NFTs as a first class citizen of its protocol. 

This feature is of great importance to our application, which places NFT creation and management at its core as a means for reliable content authentication: Since each NFT represents a unique, indivisible asset, it can be directly associated with a distinct piece of content. By publishing content through our application and correlating it with a unique NFT, we can establish an unambiguous, verifiable link between the content and its authenticated origin.

NFTs natively available on the protocol level facilitates a scalable authentication infrastructure for us: Security, speedy, reliability and low transaction costs, provide an optimal foundation for our application.

The rapid transaction confirmation time enables swift authentication and verification of content, which is critical for mitigating the spread of fraudulent digital media.

<br/>
<p align="center">
  <img src="https://github.com/deep-ink-ventures/xrp-confirmify-poc/assets/120174523/f972717d-bffd-4d50-8031-a8cee5285ba6">
</p><br />

We want to build a web2 experience with everyday users mainly unaware of blockchain technology being a key part of the underlying infrastructure. 

Ripple is the right tool for this job, with the key components of our requirements list being baked directly into the ledger.

## Setting up

This repository uses the [Django Webframework](https://www.djangoproject.com/) alongside with [a few](https://github.com/deep-ink-ventures/xrp-confirmify-poc/blob/main/requirements.txt) python libraries such as xrpl-py.

The installation should be straightforward if you are a pythonista and reasonably straightforward if not :-).

### Setting up the environment

Make sure you have at least python 3.11 installed, create a virtual environment if you do and activate it. Afterwards you can install the requirements.

```sh
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install - requirements.txt
```

Next up we need to fire up a database and a cache and the easiest no-config way of doing this is to use [docker](https://www.docker.com/). The [docker-compose](https://github.com/deep-ink-ventures/xrp-confirmify-poc/blob/main/docker-compose.yml) file is setup to work with the defaults in djangos settings.

```sh
docker compose up -d
```

Almost there. We now can create the initial migrations and run a server.

```sh
./manage.py makemigrations
./manage.py runserver
```

Visit [localhost:8000](http://localhost:8000/) to view a rudimentary interface.

> The command `./manage.py createsuperuser` let's you setup an admin here.

Another useful command is a background worker that you can ignite with `./manage.py mint_nfts`. It observes content that are submitted to the API and mints corresponding
NFTs on the XRP ledger.

### Resources

We have already created a brand guide, mockups and designs. Review them [here](https://drive.google.com/file/d/1vftwT-Bx_jiu1xau6Row-ifjVEb0SgP4/view)!

We have created a chrome extension to test this in action. Check it out [here](https://github.com/deep-ink-ventures/xrp-confirmify-ext)!






